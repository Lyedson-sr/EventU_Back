from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from apps.accounts.models import CustomUser

class AuthViewSetTest(APITestCase):
    def setUp(self):
        self.register_url = reverse('user_register')
        self.activate_url = reverse('activate_account')
        
        self.valid_registration_data = {
            'email': 'newuser@uece.br',
            'name': 'New User',
            'role': CustomUser.Role.STUDENT,
            'password': 'validpass123'
        }

    @patch('apps.accounts.services.activation_services.ActivationService.send_activation_email')
    @patch('apps.accounts.services.activation_services.ActivationService.generate_activation_code')
    def test_register_success(self, mock_generate_code, mock_send_email):
        """Testa registro bem-sucedido"""
        mock_generate_code.return_value = '1234'
        
        response = self.client.post(self.register_url, self.valid_registration_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Conta criada com sucesso. Verifique seu email para o código de ativação')
        self.assertEqual(response.data['data']['email'], 'newuser@uece.br')
        
        # Verifica que usuário foi criado
        user = CustomUser.objects.get(email='newuser@uece.br')
        self.assertFalse(user.is_active)
        
        # Verifica que email foi enviado
        mock_send_email.assert_called_once_with(user, '1234')

    def test_register_invalid_data(self):
        """Testa registro com dados inválidos"""
        invalid_data = {
            'email': 'invalid-email',
            'name': '',
            'role': 'invalid_role',
            'password': 'short'
        }
        
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('name', response.data)
        self.assertIn('role', response.data)
        self.assertIn('password', response.data)

    @patch('apps.accounts.services.activation_services.ActivationService.verify_activation_code')
    def test_activate_account_success(self, mock_verify_code):
        """Testa ativação bem-sucedida da conta"""
        # Cria usuário inativo
        user = CustomUser.objects.create_user(
            email='test@uece.br',
            name='Test User',
            role=CustomUser.Role.STUDENT,
            password='test123'
        )
        
        mock_verify_code.return_value = True
        
        activation_data = {
            'email': 'test@uece.br',
            'code': '1234'
        }
        
        response = self.client.post(self.activate_url, activation_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Conta ativada com sucesso.')
        
        # Verifica que usuário foi ativado
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Verifica que tokens foram gerados
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_activate_account_invalid_data(self):
        """Testa ativação com dados inválidos"""
        activation_data = {
            'email': 'nonexistent@uece.br',
            'code': '1234'
        }
        
        response = self.client.post(self.activate_url, activation_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)