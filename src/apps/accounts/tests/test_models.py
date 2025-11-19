from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.accounts.models import CustomUser

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@uece.br',
            'name': 'Test User',
            'role': CustomUser.Role.STUDENT,
            'password': 'testpass123'
        }

    def test_create_user_success(self):
        """Testa criação bem-sucedida de usuário"""
        user = CustomUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@uece.br')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, CustomUser.Role.STUDENT)
        self.assertFalse(user.is_active)  # Deve ser False inicialmente
        self.assertTrue(user.check_password('testpass123'))

    def test_create_user_without_email_raises_error(self):
        """Testa que criar usuário sem email levanta erro"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email=None,
                name='Test User',
                role=CustomUser.Role.STUDENT,
                password='testpass123'
            )

    def test_create_user_without_name_raises_error(self):
        """Testa que criar usuário sem nome levanta erro"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email='test@uece.br',
                name=None,
                role=CustomUser.Role.STUDENT,
                password='testpass123'
            )

    def test_create_user_without_role_raises_error(self):
        """Testa que criar usuário sem role levanta erro"""
        user = CustomUser.objects.create_user(
            email="test@uece.br",
            name="Test User",
            password="testpass123"
        )
        self.assertEqual(user.role, CustomUser.Role.STUDENT)

    def test_email_unique_constraint(self):
        """Testa que email deve ser único"""
        CustomUser.objects.create_user(**self.user_data)
        
        with self.assertRaises(Exception): 
            CustomUser.objects.create_user(**self.user_data)

    def test_role_choices(self):
        """Testa que role deve ser uma escolha válida"""
        user = CustomUser.objects.create_user(**self.user_data)
        
        # Testa choices válidas
        valid_roles = [role[0] for role in CustomUser.Role.choices]
        self.assertIn(user.role, valid_roles)
        
        # Testa choice inválida
        with self.assertRaises(ValidationError):
            user.role = 'invalid_role'
            user.full_clean()

    def test_string_representation(self):
        """Testa a representação em string do modelo"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)

    def test_preferred_calendar_view_default(self):
        """Testa o valor padrão do preferred_calendar_view"""
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.preferred_calendar_view, CustomUser.CalendarView.MONTH)