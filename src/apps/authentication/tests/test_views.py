from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.authentication.services.activation_services import ActivationService
from apps.authentication.services.password_reset_services import PasswordResetService
from apps.authentication.authentication import EmailBackend


User = get_user_model()


class AuthenticationViewsTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpass123',
            'role': 'student'
        }

    def test_user_registration_success(self):
        url = reverse('register')
        response = self.client.post(url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Conta criada com sucesso. Verifique seu email para ativação.')
        self.assertEqual(response.data['data']['email'], 'test@example.com')
        
        # Verifica se o usuário foi criado
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)
        
        # Verifica se o email foi enviado
        self.assertEqual(len(mail.outbox), 1)

    def test_user_registration_invalid_data(self):
        url = reverse('register')
        invalid_data = {
            'email': 'invalid-email',
            'name': 'Test',
            'password': 'short'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_account_success(self):
        # Cria usuário inativo
        user = User.objects.create_user(**self.user_data)
        code = ActivationService.generate_activation_code(user)
        
        url = reverse('activate-account')
        activation_data = {
            'email': user.email,
            'code': code
        }
        
        response = self.client.post(url, activation_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Conta ativada com sucesso.')
        
        # Verifica se o usuário foi ativado
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Verifica se tokens foram retornados
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_activate_account_invalid_code(self):
        user = User.objects.create_user(**self.user_data)
        
        url = reverse('activate-account')
        activation_data = {
            'email': user.email,
            'code': '0000'  # Código inválido
        }
        
        response = self.client.post(url, activation_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        # Cria usuário ativo
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        url = reverse('login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login realizado com sucesso.')
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_inactive_user(self):
        _ = User.objects.create_user(**self.user_data)  # Usuário inativo por padrão
        
        url = reverse('login')
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forgot_password_success(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        url = reverse('forgot-password')
        forgot_data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(url, forgot_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_forgot_password_nonexistent_email(self):
        url = reverse('forgot-password')
        forgot_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post(url, forgot_data)
        # Deve retornar sucesso mesmo para email não existente (por segurança)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inform_code_success(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        code = PasswordResetService.generate_reset_code(user.id)
        
        url = reverse('inform-code')
        inform_code_data = {
            'email': user.email,
            'code': code
        }
        
        response = self.client.post(url, inform_code_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Código validado com sucesso. Você pode redefinir sua senha.')

    def test_inform_code_invalid(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        PasswordResetService.generate_reset_code(user.id)
        
        url = reverse('inform-code')
        inform_code_data = {
            'email': user.email,
            'code': '0000'  # Código inválido
        }
        
        response = self.client.post(url, inform_code_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_success(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        # Simula o fluxo completo: gera código e valida
        code = PasswordResetService.generate_reset_code(user.id)
        PasswordResetService.verify_code(user.email, code)
        
        url = reverse('reset-password')
        reset_data = {
            'email': user.email,
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(url, reset_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Senha redefinida com sucesso.')
        
        # Verifica se a senha foi alterada
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))

    def test_reset_password_without_code_validation(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        url = reverse('reset-password')
        reset_data = {
            'email': user.email,
            'new_password': 'newpassword123'
        }
        
        response = self.client.post(url, reset_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        user = User.objects.create_user(**self.user_data)
        user.is_active = True
        user.save()
        
        # Login para obter tokens
        login_url = reverse('login')
        login_response = self.client.post(login_url, {
            'email': user.email,
            'password': 'testpass123'
        })
        
        refresh_token = login_response.data['tokens']['refresh']
        access_token = login_response.data['tokens']['access']
        
        # Logout with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_url = reverse('logout')
        logout_data = {
            'refresh_token': refresh_token
        }
        
        response = self.client.post(logout_url, logout_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_invalid_token(self):
        url = reverse('logout')
        response = self.client.post(url, {'refresh_token': 'invalid-token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailBackendTest(TestCase):
    def setUp(self):
        self.backend = EmailBackend()
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123',
            is_active=True
        )

    def test_authenticate_success(self):
        user = self.backend.authenticate(
            request=None,
            username='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user, self.user)

    def test_authenticate_wrong_password(self):
        user = self.backend.authenticate(
            request=None,
            username='test@example.com',
            password='wrongpassword'
        )
        self.assertIsNone(user)

    def test_authenticate_nonexistent_user(self):
        user = self.backend.authenticate(
            request=None,
            username='nonexistent@example.com',
            password='testpass123'
        )
        self.assertIsNone(user)

    def test_authenticate_inactive_user(self):
        _ = User.objects.create_user(
            email='inactive@example.com',
            name='Inactive User',
            password='testpass123',
            is_active=False
        )
        
        user = self.backend.authenticate(
            request=None,
            username='inactive@example.com',
            password='testpass123'
        )
        self.assertIsNone(user)

    def test_get_user_success(self):
        user = self.backend.get_user(self.user.id)
        self.assertEqual(user, self.user)

    def test_get_user_nonexistent(self):
        user = self.backend.get_user(9999)
        self.assertIsNone(user)