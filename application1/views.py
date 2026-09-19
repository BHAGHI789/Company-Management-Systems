import json
import hashlib
import logging
import secrets
from datetime import  timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from .models import *
from django.conf import settings as django_settings
import pandas as pd
import base64
from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization


KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"   # adjust path if needed
print("KEYS_DIR", KEYS_DIR)
with open(KEYS_DIR / "private_key.pem", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(KEYS_DIR / "public_key.pem", "rb") as f:
    PUBLIC_KEY_PEM = f.read()          # we will send the DER form to frontend


def get_public_key_der_b64():
    """Return pure Base64 DER of the public key (what Web Crypto wants)."""
    public_key = PRIVATE_KEY.public_key()
    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return base64.b64encode(der).decode("ascii")


def decrypt_value(encrypted_b64: str) -> str:
    """Decrypt a value that was encrypted with the public key on the frontend."""
    if not encrypted_b64:
        raise ValueError("Empty encrypted value")

    # Frontend sometimes replaces + with space in transit
    encrypted_b64 = encrypted_b64.replace(" ", "+")
    encrypted_bytes = base64.b64decode(encrypted_b64)

    # Web Crypto uses RSA-OAEP with SHA-256
    decrypted = PRIVATE_KEY.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode("utf-8")


# -------------------------------------------------
# Views
# -------------------------------------------------
def get_public_key(request):
    return JsonResponse({
        "public_key": get_public_key_der_b64()
    })




class Login(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self,request, *args, **kwargs):
        logout(request)
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        contenttype = request.META.get('CONTENT_TYPE', None)
        data_dict = None
        if 'json' in contenttype:
            #log.debug("json request body is %s", request.body)
            try:
                data_dict = json.loads(request.body.decode('utf-8'))
            except Exception as e:
                log.exception(e)
        elif contenttype == 'application/x-www-form-urlencoded':
            log.debug("content type is application/x-www-form-urlencoded ")
            data_dict = request.POST
        else:
            log.debug('Unknown ContentType: %s', contenttype)
            pdr = HttpResponse(status=400)
            pdr.write('Unknown HTTP ContentTye')
            return pdr
        try:
            if data_dict.get("status") == "credentials_verified":
                print("credentials")
                email = decrypt_value(data_dict.get("email"))
                password = decrypt_value(data_dict.get("password"))
                

                user = get_user_model().objects.filter(email__iexact=email).first()
                authenticated_user = (
                    authenticate(request, username=user.username, password=password)
                    if user is not None else None
                )

                if authenticated_user:


                    otp = secrets.randbelow(900000) + 100000
                    print("Generated OTP:", otp)
                    OTPValues.objects.update_or_create(
                        email=authenticated_user.email,
                        defaults={
                            "otp": str(otp),
                            "createdBy": authenticated_user,
                            "updatedBy": authenticated_user,
                        }
                    )
                    request.session['login_otp'] = {
                        "user_id": str(authenticated_user.pk),
                        "otp_hash": hashlib.sha256(str(otp).encode()).hexdigest(),
                        "expires_at": (timezone.now() + timedelta(minutes=10)).isoformat(),
                    }
                    resp = HttpResponse(content_type="application/json", status=200)
                    resp.write(json.dumps({"success": True, "status": "otp_sent"}))
                    return resp


                resp = HttpResponse(content_type="application/json", status=401)
                resp.write(json.dumps({"success": False, "message": "Invalid email or password."}))
                return resp
            if data_dict.get("status") == "otp_verify_testing":

                login_otp = request.session.get('login_otp')
                otp = str(data_dict.get("otp", "")).strip()
                if not login_otp:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Request a new OTP first."}))
                    return resp



                
            if data_dict.get("status") == "otp_verify":
                login_otp = request.session.get('login_otp')
                otp = str(data_dict.get("otp", "")).strip()

                if not login_otp:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Request a new OTP first."}))
                    return resp

                if timezone.now() > timezone.datetime.fromisoformat(login_otp["expires_at"]):
                    request.session.pop('login_otp', None)
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "This OTP has expired."}))
                    return resp

                if not secrets.compare_digest(hashlib.sha256(otp.encode()).hexdigest(), login_otp["otp_hash"]):
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Invalid OTP."}))
                    return resp

                otp_user = get_user_model().objects.filter(pk=login_otp["user_id"]).first()
                request.session.pop('login_otp', None)
                if otp_user is None:
                    resp = HttpResponse(content_type="application/json", status=400)
                    resp.write(json.dumps({"success": False, "message": "Account was not found."}))
                    return resp

                # login() creates the session; Django sends the sessionid cookie with this response
                login(request, otp_user)
                resp = HttpResponse(content_type="application/json", status=200)
                resp.write(json.dumps({"success": True, "status": "signed_in"}))
                return resp

            resp = HttpResponse(content_type="application/json", status=200)
            resp.write(json.dumps({"znid": "znobj.id", "details": data_dict}))
            return resp
        except Exception as e:
            print(f"Exception occurred: {e}")
            resp = HttpResponse(json.dumps(data_dict), content_type='application/json', status=400)
            return resp


class EmployeeList(View):
    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        # employeesDf = pd.DataFrame(Employees.objects.all().values("employeeName", "employeeId", "employeeEmail", "employeePhone", "employeeAddress", "employeeDepartment", "employeeDesignation", "employeeSalary", "employeeJoiningDate", "employeeStatus", "employeeCreatedAt", "employeeUpdatedAt"))
        
        return render(request, 'employeeList.html', locals())
