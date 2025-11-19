from django.test import TestCase
from django.core.cache import cache
from unittest.mock import patch
from apps.accounts.models import CustomUser
from ..services.activation_services import ActivationService

class ActivationServiceTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@uece.br',
            name='Test User',
            role=CustomUser.Role.STUDENT,
            password='test123'
        )

    def test_generate_activation_code(self):
        """Testa geração de código de ativação"""
        code = ActivationService.generate_activation_code(self.user.id)
        
        self.assertEqual(len(code), 4)
        self.assertTrue(code.isdigit())
        
        # Verifica se foi salvo no cache
        cached_code = cache.get(f'activation_code_{self.user.id}')
        self.assertEqual(code, cached_code)

    def test_verify_activation_code_valid(self):
        """Testa verificação de código válido"""
        # Configura código no cache
        cache.set(f'activation_code_{self.user.id}', '1234', 3600)
        
        result = ActivationService.verify_activation_code(self.user.id, '1234')
        self.assertTrue(result)
        
        # Verifica que código foi removido do cache após uso
        cached_code = cache.get(f'activation_code_{self.user.id}')
        self.assertIsNone(cached_code)

    def test_verify_activation_code_invalid(self):
        """Testa verificação de código inválido"""
        cache.set(f'activation_code_{self.user.id}', '1234', 3600)
        
        result = ActivationService.verify_activation_code(self.user.id, '9999')
        self.assertFalse(result)

    def test_verify_activation_code_expired(self):
        """Testa verificação de código expirado"""
        cache.delete(f'activation_code_{self.user.id}')  # garante que não existe código
        result = ActivationService.verify_activation_code(self.user.id, '1234')
        self.assertFalse(result)

    @patch('apps.accounts.services.activation_services.send_mail')
    def test_send_activation_email(self, mock_send_mail):
        """Testa envio de email de ativação"""
        ActivationService.send_activation_email(self.user, '1234')
        
        # Verifica que send_mail foi chamado corretamente
        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args
        self.assertEqual(call_args[1]['subject'], 'Ative sua conta no EventU')
        self.assertIn('1234', call_args[1]['message'])
        self.assertEqual(call_args[1]['recipient_list'], ['test@uece.br'])