from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from apps.accounts.models import CustomUser


class AuthViewSetTest(APITestCase):
    def setUp(self):
        # CORREÇÃO: Adicione o login_url aqui
        self.register_url = reverse("user_register")
        self.activate_url = reverse("activate_account")
        self.login_url = reverse("login") 

        self.valid_registration_data = {
            "email": "newuser@uece.br",
            "name": "New User",
            "role": CustomUser.Role.STUDENT,
            "password": "validpass123",
        }

        # Cria usuário para testes de login
        self.user = CustomUser.objects.create_user(
            email="activeuser@uece.br",
            name="Active User",
            role=CustomUser.Role.STUDENT,
            password="testpass123",
        )
        self.user.is_active = True
        self.user.save()

    @patch(
        "apps.accounts.services.activation_services.ActivationService.send_activation_email"
    )
    @patch(
        "apps.accounts.services.activation_services.ActivationService.generate_activation_code"
    )
    def test_register_success(self, mock_generate_code, mock_send_email):
        """Testa registro bem-sucedido"""
        mock_generate_code.return_value = "1234"

        response = self.client.post(self.register_url, self.valid_registration_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["message"],
            "Conta criada com sucesso. Verifique seu email para o código de ativação",
        )
        self.assertEqual(response.data["data"]["email"], "newuser@uece.br")

        # Verifica que usuário foi criado
        user = CustomUser.objects.get(email="newuser@uece.br")
        self.assertFalse(user.is_active)

        # Verifica que email foi enviado
        mock_send_email.assert_called_once_with(user, "1234")

    def test_register_invalid_data(self):
        """Testa registro com dados inválidos"""
        invalid_data = {
            "email": "invalid-email",
            "name": "",
            "role": "invalid_role",
            "password": "short",
        }

        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # CORREÇÃO: Ajuste para a estrutura do drf-standardized-errors
        self.assertEqual(response.data["type"], "validation_error")
        errors = {error["attr"]: error for error in response.data["errors"]}

        self.assertIn("email", errors)
        self.assertIn("name", errors)
        self.assertIn("role", errors)
        self.assertIn("password", errors)

    @patch(
        "apps.accounts.services.activation_services.ActivationService.verify_activation_code"
    )
    def test_activate_account_success(self, mock_verify_code):
        """Testa ativação bem-sucedida da conta"""
        # Cria usuário inativo
        user = CustomUser.objects.create_user(
            email="test@uece.br",
            name="Test User",
            role=CustomUser.Role.STUDENT,
            password="test123",
        )

        mock_verify_code.return_value = True

        activation_data = {"email": "test@uece.br", "code": "1234"}

        response = self.client.post(self.activate_url, activation_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Conta ativada com sucesso.")

        # Verifica que usuário foi ativado
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        # Verifica que tokens foram gerados
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_activate_account_invalid_data(self):
        """Testa ativação com dados inválidos"""
        activation_data = {"email": "nonexistent@uece.br", "code": "1234"}

        response = self.client.post(self.activate_url, activation_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TESTES PARA LOGIN (AGORA CORRETOS)
    def test_login_success(self):
        """Testa login bem-sucedido"""
        login_data = {"email": "activeuser@uece.br", "password": "testpass123"}

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Login realizado com sucesso.")

        # Verifica dados do usuário
        self.assertEqual(response.data["data"]["email"], "activeuser@uece.br")
        self.assertEqual(response.data["data"]["name"], "Active User")

        # Verifica que tokens foram gerados
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

        # Verifica que tokens são válidos
        access_token = response.data["tokens"]["access"]
        self.assertTrue(access_token.startswith("eyJ"))  # JWT tokens começam com eyJ

    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas"""
        login_data = {"email": "activeuser@uece.br", "password": "wrongpassword"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["type"], "client_error")
        # Pode verificar a mensagem específica se quiser

    def test_login_nonexistent_user(self):
        """Testa login com usuário inexistente"""
        login_data = {"email": "nonexistent@uece.br", "password": "anypassword"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["type"], "client_error")

    def test_login_inactive_user(self):
        """Testa login com usuário inativo"""
        # Cria usuário inativo
        _ = CustomUser.objects.create_user(
            email="inactive@uece.br",
            name="Inactive User",
            role=CustomUser.Role.STUDENT,
            password="testpass123",
        )
        # Não ativa o usuário (is_active=False por padrão)

        login_data = {"email": "inactive@uece.br", "password": "testpass123"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["type"], "client_error")

    def test_login_missing_fields(self):
        """Testa login com campos faltando"""
        # Sem email
        login_data = {"password": "testpass123"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["type"], "validation_error")

        errors = {error["attr"]: error for error in response.data["errors"]}
        self.assertIn("email", errors)

        # Sem password
        login_data = {"email": "activeuser@uece.br"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["type"], "validation_error")

        errors = {error["attr"]: error for error in response.data["errors"]}
        self.assertIn("password", errors)

    def test_login_invalid_email_format(self):
        """Testa login com formato de email inválido"""
        login_data = {"email": "invalid-email", "password": "testpass123"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["type"], "validation_error")

        errors = {error["attr"]: error for error in response.data["errors"]}
        self.assertIn("email", errors)

    def test_login_case_insensitive_email(self):
        """Testa que login não é case insensitive para email"""
        login_data = {
            "email": "ACTIVEUSER@uece.br",  # Email em uppercase
            "password": "testpass123",
        }

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["type"], "client_error")

    def test_login_different_user_roles(self):
        """Testa login com diferentes roles de usuário"""
        # Cria usuário professor
        professor = CustomUser.objects.create_user(
            email="professor@uece.br",
            name="Professor User",
            role=CustomUser.Role.PROFESSOR,
            password="testpass123",
        )
        professor.is_active = True
        professor.save()

        login_data = {"email": "professor@uece.br", "password": "testpass123"}

        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["role"], CustomUser.Role.PROFESSOR)
