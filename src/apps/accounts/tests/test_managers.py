from django.test import TestCase
from apps.accounts.models import CustomUser

class CustomUserManagerTest(TestCase):
    def test_create_user(self):
        """Testa a criação de usuário normal pelo manager"""
        user = CustomUser.objects.create_user(
            email='user@uece.br',
            name='Regular User',
            role=CustomUser.Role.STUDENT,
            password='password123'
        )
        
        self.assertEqual(user.email, 'user@uece.br')
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password('password123'))

    def test_create_superuser(self):
        """Testa a criação de superusuário"""
        superuser = CustomUser.objects.create_superuser(
            email='admin@uece.br',
            name='Admin User',
            role=CustomUser.Role.ADMIN,
            password='admin123'
        )
        
        self.assertEqual(superuser.email, 'admin@uece.br')
        self.assertTrue(superuser.is_active)

    def test_create_user_with_extra_fields(self):
        """Testa criação de usuário com campos extras"""
        user = CustomUser.objects.create_user(
            email='test@uece.br',
            name='Test User',
            role=CustomUser.Role.PROFESSOR,
            password='test123',
            preferred_calendar_view=CustomUser.CalendarView.WEEK
        )
        
        self.assertEqual(user.preferred_calendar_view, CustomUser.CalendarView.WEEK)