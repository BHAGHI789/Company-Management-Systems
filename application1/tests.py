
import base64
import hashlib
from datetime import timedelta
from unittest.mock import patch
import uuid
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import OTPValues


class LoginViewTests(TestCase):

    def setUp(self):
        self.login_url = reverse("login")

        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Test@12345",
        )

    # ---------------------------------------------------------
    # GET / LOGIN PAGE
    # ---------------------------------------------------------

    def test_login_get_page(self):
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_get_logs_out_existing_user(self):
        self.client.force_login(self.user)

        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)

        session = self.client.session
        self.assertNotIn("_auth_user_id", session)

    # ---------------------------------------------------------
    # CREDENTIAL LOGIN
    # ---------------------------------------------------------

    @patch("application1.views.decrypt_value")
    def test_login_with_valid_credentials_sends_otp(
        self,
        mock_decrypt,
    ):
        mock_decrypt.side_effect = [
            "test@example.com",
            "Test@12345",
        ]

        response = self.client.post(
            self.login_url,
            data={
                "status": "credentials_verified",
                "email": "encrypted-email",
                "password": "encrypted-password",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertTrue(response_data["success"])
        self.assertEqual(
            response_data["status"],
            "otp_sent",
        )

        otp_record = OTPValues.objects.filter(
            email="test@example.com"
        ).first()

        self.assertIsNotNone(otp_record)
        self.assertEqual(otp_record.createdBy, self.user)

        session = self.client.session

        self.assertIn("login_otp", session)

        login_otp = session["login_otp"]

        self.assertEqual(
            login_otp["user_id"],
            str(self.user.pk),
        )

        self.assertIn("otp_hash", login_otp)
        self.assertIn("expires_at", login_otp)

    @patch("application1.views.decrypt_value")
    def test_login_with_invalid_credentials(
        self,
        mock_decrypt,
    ):
        mock_decrypt.side_effect = [
            "test@example.com",
            "WrongPassword@123",
        ]

        response = self.client.post(
            self.login_url,
            data={
                "status": "credentials_verified",
                "email": "encrypted-email",
                "password": "encrypted-password",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

        response_data = response.json()

        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"],
            "Invalid email or password.",
        )

    @patch("application1.views.decrypt_value")
    def test_login_with_unknown_email(
        self,
        mock_decrypt,
    ):
        mock_decrypt.side_effect = [
            "unknown@example.com",
            "Test@12345",
        ]

        response = self.client.post(
            self.login_url,
            data={
                "status": "credentials_verified",
                "email": "encrypted-email",
                "password": "encrypted-password",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

        response_data = response.json()

        self.assertFalse(response_data["success"])

    # ---------------------------------------------------------
    # OTP VERIFICATION
    # ---------------------------------------------------------

    def create_otp_session(self, otp="123456", minutes=10):

        session = self.client.session

        session["login_otp"] = {
            "user_id": str(self.user.pk),
            "otp_hash": hashlib.sha256(
                otp.encode()
            ).hexdigest(),
            "expires_at": (
                timezone.now()
                + timedelta(minutes=minutes)
            ).isoformat(),
        }

        session.save()

    def test_otp_verification_without_session(self):

        response = self.client.post(
            self.login_url,
            data={
                "status": "otp_verify",
                "otp": "123456",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()

        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"],
            "Request a new OTP first.",
        )

    def test_otp_verification_with_invalid_otp(self):

        self.create_otp_session(
            otp="123456"
        )

        response = self.client.post(
            self.login_url,
            data={
                "status": "otp_verify",
                "otp": "999999",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()

        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"],
            "Invalid OTP.",
        )

    def test_otp_verification_with_expired_otp(self):

        self.create_otp_session(
            otp="123456",
            minutes=-10,
        )

        response = self.client.post(
            self.login_url,
            data={
                "status": "otp_verify",
                "otp": "123456",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()

        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"],
            "This OTP has expired.",
        )

        session = self.client.session

        self.assertNotIn(
            "login_otp",
            session,
        )

    def test_otp_verification_with_valid_otp(self):

        self.create_otp_session(
            otp="123456"
        )

        response = self.client.post(
            self.login_url,
            data={
                "status": "otp_verify",
                "otp": "123456",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertTrue(response_data["success"])
        self.assertEqual(
            response_data["status"],
            "signed_in",
        )

        session = self.client.session

        self.assertNotIn(
            "login_otp",
            session,
        )

        self.assertEqual(
            str(session["_auth_user_id"]),
            str(self.user.pk),
        )

    def test_otp_verification_user_not_found(self):
        session = self.client.session

        session["login_otp"] = {
            "user_id": str(uuid.uuid4()),
            "otp_hash": hashlib.sha256(b"123456").hexdigest(),
            "expires_at": (
                timezone.now() + timedelta(minutes=10)
            ).isoformat(),
        }

        session.save()

        response = self.client.post(
            self.login_url,
            data={
                "status": "otp_verify",
                "otp": "123456",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        response_data = response.json()

        self.assertFalse(response_data["success"])
        self.assertEqual(
            response_data["message"],
            "Account was not found.",
        )# ---------------------------------------------------------
        # PUBLIC KEY
    # ---------------------------------------------------------

    def test_get_public_key(self):

        response = self.client.get(
            reverse("get_public_key")
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()

        self.assertIn(
            "public_key",
            response_data,
        )

        self.assertTrue(
            len(response_data["public_key"]) > 0
        )

        # Verify it is valid Base64
        decoded_key = base64.b64decode(
            response_data["public_key"]
        )

        self.assertTrue(
            len(decoded_key) > 0
        )

    # ---------------------------------------------------------
    # EMPLOYEE LIST
    # ---------------------------------------------------------

    def test_employee_list(self):

        response = self.client.get(
            reverse("employee_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "employeeList.html",
        )
