from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from api.models import Company
from app_auth.models import CompanyUser


class CompanyUserManagerTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

    def test_create_user(self):
        user = CompanyUser.objects.create_user(email='normal@user.com', password='foo')
        self.assertEqual(user.email, 'normal@user.com')
        self.assertTrue(user.check_password('foo'))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_create_user_no_email(self):
        with self.assertRaises(ValueError):
            CompanyUser.objects.create_user(email=None, password='foo')

    def test_create_superuser(self):
        superuser = CompanyUser.objects.create_superuser(email='super@user.com', password='foo')
        self.assertEqual(superuser.email, 'super@user.com')
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.check_password('foo'))

    def test_create_superuser_invalid_flags(self):
        with self.assertRaises(ValueError):
            CompanyUser.objects.create_superuser(email='super2@user.com', password='foo', is_staff=False)
        with self.assertRaises(ValueError):
            CompanyUser.objects.create_superuser(email='super3@user.com', password='foo', is_superuser=False)

    def test_user_str(self):
        user = CompanyUser.objects.create_user(email='test@user.com', password='foo')
        self.assertEqual(str(user), 'test@user.com')


class CompanyUserModelTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Test Company")

    def test_user_creation_with_company(self):
        user = CompanyUser.objects.create_user(email='link@company.com', password='foo', company=self.company)
        self.assertEqual(user.company, self.company)

    def test_email_unique(self):
        CompanyUser.objects.create_user(email='unique@user.com', password='foo')
        with self.assertRaises(IntegrityError):
            CompanyUser.objects.create_user(email='unique@user.com', password='bar')
