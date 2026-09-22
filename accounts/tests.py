from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse("register"), {
            "username": "karar_ver",
            "email": "karar@example.com",
            "password": "cok-guclu-parola-123",
            "password_confirm": "cok-guclu-parola-123",
        })
        self.assertRedirects(response, reverse("poll_list"))
        self.assertTrue(User.objects.filter(username="karar_ver").exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username="ilk_kullanici", email="ayni@example.com", password="parola12345")
        response = self.client.post(reverse("register"), {
            "username": "ikinci_kullanici",
            "email": "ayni@example.com",
            "password": "cok-guclu-parola-123",
            "password_confirm": "cok-guclu-parola-123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", "Bu e-posta adresi zaten kayıtlı.")

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="ayni_kullanici", email="birinci@example.com", password="parola12345")
        response = self.client.post(reverse("register"), {
            "username": "ayni_kullanici",
            "email": "ikinci@example.com",
            "password": "cok-guclu-parola-123",
            "password_confirm": "cok-guclu-parola-123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "username", "Bu kullanıcı adı zaten alınmış.")


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="deneme_kullanici",
            email="deneme@example.com",
            password="cok-guclu-parola-123",
        )

    def test_login_with_email(self):
        response = self.client.post(reverse("login"), {
            "identifier": "deneme@example.com",
            "password": "cok-guclu-parola-123",
        })
        self.assertRedirects(response, reverse("poll_list"))

    def test_login_with_username(self):
        response = self.client.post(reverse("login"), {
            "identifier": "deneme_kullanici",
            "password": "cok-guclu-parola-123",
        })
        self.assertRedirects(response, reverse("poll_list"))

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(reverse("login"), {
            "identifier": "deneme_kullanici",
            "password": "yanlis-parola",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
