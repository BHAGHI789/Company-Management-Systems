import base64
import hashlib
import json
import logging
import secrets
from datetime import timedelta
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View

from .models import OTPValues


log = logging.getLogger(__name__)

KEYS_DIR = Path(__file__).resolve().parent.parent / "keys"

with open(KEYS_DIR / "private_key.pem", "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(
        f.read(),
        password=None,
    )

with open(KEYS_DIR / "public_key.pem", "rb") as f:
    PUBLIC_KEY_PEM = f.read()


def get_public_key_der_b64():
    """Return Base64 DER of the public key for Web Crypto."""
    public_key = PRIVATE_KEY.public_key()

    der = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return base64.b64encode(der).decode("ascii")


def decrypt_value(encrypted_b64: str) -> str:
    """Decrypt a value encrypted with the public key on the frontend."""
    if not encrypted_b64:
        raise ValueError("Empty encrypted value")

    # Frontend sometimes replaces + with space in transit.
    encrypted_b64 = encrypted_b64.replace(" ", "+")

    encrypted_bytes = base64.b64decode(encrypted_b64)

    # Web Crypto uses RSA-OAEP with SHA-256.
    decrypted = PRIVATE_KEY.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    return decrypted.decode("utf-8")


def get_public_key(request):
    return JsonResponse(
        {
            "public_key": get_public_key_der_b64(),
        }
    )


class Login(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        logout(request)
        return render(request, "login.html")

    @staticmethod
    def json_response(data, status=200):
        return HttpResponse(
            json.dumps(data),
            content_type="application/json",
            status=status,
        )

    def post(self, request, *args, **kwargs):
        try:
            data_dict = self.get_request_data(request)

            status = data_dict.get("status")

            if status == "credentials_verified":
                return self.handle_credentials(request, data_dict)

            if status == "otp_verify_testing":
                return self.handle_otp_testing(request, data_dict)

            if status == "otp_verify":
                return self.handle_otp_verification(request, data_dict)

            return self.json_response(
                {
                    "znid": "znobj.id",
                    "details": data_dict,
                }
            )

        except Exception:
            log.exception("Exception occurred while processing login request")

            return self.json_response(
                {
                    "success": False,
                    "message": "An unexpected error occurred.",
                },
                status=400,
            )

    @staticmethod
    def get_request_data(request):
        content_type = request.META.get("CONTENT_TYPE", "")

        if "json" in content_type:
            try:
                return json.loads(request.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                log.exception("Invalid JSON request body")

                raise ValueError("Invalid JSON request.")

        if content_type == "application/x-www-form-urlencoded":
            log.debug("Content type is application/x-www-form-urlencoded")
            return request.POST

        log.debug("Unknown Content-Type: %s", content_type)
        raise ValueError("Unknown HTTP Content-Type")

    def handle_credentials(self, request, data_dict):
        email = decrypt_value(data_dict.get("email"))
        password = decrypt_value(data_dict.get("password"))

        user = (
            get_user_model()
            .objects.filter(email__iexact=email)
            .first()
        )

        if user is None:
            return self.invalid_credentials_response()

        authenticated_user = authenticate(
            request,
            username=user.username,
            password=password,
        )

        if authenticated_user is None:
            return self.invalid_credentials_response()

        otp = self.generate_otp(authenticated_user)

        self.store_login_otp(
            request,
            authenticated_user,
            otp,
        )

        return self.json_response(
            {
                "success": True,
                "status": "otp_sent",
            }
        )

    def generate_otp(self, user):
        otp = secrets.randbelow(900000) + 100000

        OTPValues.objects.update_or_create(
            email=user.email,
            defaults={
                "otp": str(otp),
                "createdBy": user,
                "updatedBy": user,
            },
        )

        return otp

    @staticmethod
    def store_login_otp(request, user, otp):
        request.session["login_otp"] = {
            "user_id": str(user.pk),
            "otp_hash": hashlib.sha256(
                str(otp).encode()
            ).hexdigest(),
            "expires_at": (
                timezone.now() + timedelta(minutes=10)
            ).isoformat(),
        }

    def invalid_credentials_response(self):
        return self.json_response(
            {
                "success": False,
                "message": "Invalid email or password.",
            },
            status=401,
        )

    def handle_otp_testing(self, request, data_dict):
        login_otp = request.session.get("login_otp")
        otp = str(data_dict.get("otp", "")).strip()

        if not login_otp:
            return self.otp_required_response()

        return self.json_response(
            {
                "success": True,
                "status": "otp_verify_testing",
                "otp": otp,
            }
        )

    def handle_otp_verification(self, request, data_dict):
        login_otp = request.session.get("login_otp")
        otp = str(data_dict.get("otp", "")).strip()

        if not login_otp:
            return self.otp_required_response()

        if self.is_otp_expired(login_otp):
            request.session.pop("login_otp", None)

            return self.json_response(
                {
                    "success": False,
                    "message": "This OTP has expired.",
                },
                status=400,
            )

        if not self.is_valid_otp(otp, login_otp):
            return self.json_response(
                {
                    "success": False,
                    "message": "Invalid OTP.",
                },
                status=400,
            )

        return self.login_otp_user(request, login_otp)

    def otp_required_response(self):
        return self.json_response(
            {
                "success": False,
                "message": "Request a new OTP first.",
            },
            status=400,
        )

    @staticmethod
    def is_otp_expired(login_otp):
        expires_at = timezone.datetime.fromisoformat(
            login_otp["expires_at"]
        )

        return timezone.now() > expires_at

    @staticmethod
    def is_valid_otp(otp, login_otp):
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        return secrets.compare_digest(
            otp_hash,
            login_otp["otp_hash"],
        )

    def login_otp_user(self, request, login_otp):
        otp_user = (
            get_user_model()
            .objects.filter(pk=login_otp["user_id"])
            .first()
        )

        request.session.pop("login_otp", None)

        if otp_user is None:
            return self.json_response(
                {
                    "success": False,
                    "message": "Account was not found.",
                },
                status=400,
            )

        login(request, otp_user)

        return self.json_response(
            {
                "success": True,
                "status": "signed_in",
            }
        )


class EmployeeList(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "employeeList.html",
            locals(),
        )
