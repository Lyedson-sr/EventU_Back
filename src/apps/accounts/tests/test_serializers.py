from django.test import TestCase
from apps.accounts.models import CustomUser
from ..serializers import UserRegistrationSerializer, UserActivationSerializer

class UserRegistrationSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'email': 'newuser@uece.br',
            'name': 'New User',
            'role': CustomUser.Role.STUDENT,
            'password': 'validpass123'
        }

    def test_valid_registration_data(self):
        """Testa dados válidos para registro"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_registration_with_existing_email(self):
        """Testa que email duplicado é rejeitado"""
        # Cria primeiro usuário
        CustomUser.objects.create_user(**self.valid_data)
        
        # Tenta criar segundo com mesmo email
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_password_min_length_validation(self):
        """Testa validação de tamanho mínimo da senha"""
        invalid_data = self.valid_data.copy()
        invalid_data['password'] = 'short'
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user_method(self):
        """Testa que o método create cria um usuário corretamente"""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        serializer.is_valid()
        user = serializer.save()
        
        self.assertEqual(user.email, 'newuser@uece.br')
        self.assertFalse(user.is_active)  # Deve estar inativo inicialmente
        self.assertTrue(user.check_password('validpass123'))

class UserActivationSerializerTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@uece.br',
            name='Test User',
            role=CustomUser.Role.STUDENT,
            password='test123'
        )
        
        # Simula código no cache
        from django.core.cache import cache
        cache.set(f'activation_code_{self.user.id}', '1234', 3600)

    def test_valid_activation_data(self):
        """Testa dados válidos para ativação"""
        data = {
            'email': 'test@uece.br',
            'code': '1234'
        }
        serializer = UserActivationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_activation_with_invalid_email(self):
        """Testa ativação com email inexistente"""
        data = {
            'email': 'nonexistent@uece.br',
            'code': '1234'
        }
        serializer = UserActivationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_activation_with_invalid_code(self):
        """Testa ativação com código inválido"""
        data = {
            'email': 'test@uece.br',
            'code': '9999'  # Código errado
        }
        serializer = UserActivationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_activation_already_active_user(self):
        """Testa ativação de usuário já ativo"""
        self.user.is_active = True
        self.user.save()
        
        data = {
            'email': 'test@uece.br',
            'code': '1234'
        }
        serializer = UserActivationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)