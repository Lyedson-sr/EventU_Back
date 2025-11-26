from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core import mail
from django.core.cache import cache
from apps.authentication.services.activation_services import ActivationService
from apps.authentication.services.password_reset_services import PasswordResetService


User = get_user_model()


class ActivationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )

    def test_generate_activation_code(self):
        code = ActivationService.generate_activation_code(self.user)
        self.assertEqual(len(code), 4)
        self.assertTrue(code.isdigit())

    def test_verify_activation_code_valid(self):
        code = ActivationService.generate_activation_code(self.user)
        self.assertTrue(ActivationService.verify_activation_code(self.user.id, code))

    def test_verify_activation_code_invalid(self):
        ActivationService.generate_activation_code(self.user)
        self.assertFalse(ActivationService.verify_activation_code(self.user.id, '0000'))

    def test_verify_activation_code_expired(self):
        code = ActivationService.generate_activation_code(self.user)
        cache.delete(f"activation_code_{self.user.id}")
        self.assertFalse(ActivationService.verify_activation_code(self.user.id, code))

    def test_send_activation_email(self):
        code = '1234'
        ActivationService.send_activation_email(self.user, code)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Ative sua conta no EventU')
        self.assertIn(code, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.user.email])


class PasswordResetServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123',
            is_active=True
        )

    def test_generate_reset_code(self):
        code = PasswordResetService.generate_reset_code(self.user.id)
        self.assertEqual(len(code), 4)
        self.assertTrue(code.isdigit())

    def test_verify_code_valid(self):
        code = PasswordResetService.generate_reset_code(self.user.id)
        self.assertTrue(PasswordResetService.verify_code(self.user.email, code))

    def test_verify_code_invalid(self):
        PasswordResetService.generate_reset_code(self.user.id)
        self.assertFalse(PasswordResetService.verify_code(self.user.email, '0000'))

    def test_verify_code_nonexistent_user(self):
        self.assertFalse(PasswordResetService.verify_code('nonexistent@example.com', '1234'))

    def test_send_reset_email(self):
        PasswordResetService.send_reset_email(self.user)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Código de redefinição de senha')
        self.assertEqual(mail.outbox[0].to, [self.user.email])

    def test_reset_password_success(self):
        code = PasswordResetService.generate_reset_code(self.user.id)
        PasswordResetService.verify_code(self.user.email, code)  # Simula validação prévia
        
        updated_user = PasswordResetService.reset_password(
            self.user.email, 'newpassword123'
        )
        
        self.assertTrue(updated_user.check_password('newpassword123'))
        self.assertIsNone(cache.get(f"password_reset_{self.user.id}"))

    def test_reset_password_no_validated_code(self):
        with self.assertRaises(ValueError):
            PasswordResetService.reset_password(self.user.email, 'newpassword123')