"""
Tests pour les modèles de base
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import BaseModel, TimestampedModel, SoftDeleteModel

User = get_user_model()


class BaseModelTest(TestCase):
    """Tests pour BaseModel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_base_model_creation(self):
        """Test de création d'un modèle de base"""
        # Crée un modèle de base simple
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, 'Test')
    
    def test_base_model_str(self):
        """Test de la méthode __str__"""
        class TestModel(BaseModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        self.assertIn('TestModel', str(obj))
        self.assertIn(str(obj.id), str(obj))


class TimestampedModelTest(TestCase):
    """Tests pour TimestampedModel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_timestamped_model_creation(self):
        """Test de création d'un modèle avec timestamps"""
        class TestModel(TimestampedModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)
        self.assertEqual(obj.created_at, obj.updated_at)
    
    def test_timestamped_model_age(self):
        """Test de la propriété age"""
        class TestModel(TimestampedModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        age = obj.age
        self.assertGreaterEqual(age, 0)
    
    def test_timestamped_model_is_recent(self):
        """Test de la propriété is_recent"""
        class TestModel(TimestampedModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        self.assertTrue(obj.is_recent)


class SoftDeleteModelTest(TestCase):
    """Tests pour SoftDeleteModel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_soft_delete_model_creation(self):
        """Test de création d'un modèle avec suppression douce"""
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        self.assertFalse(obj.is_deleted)
        self.assertIsNone(obj.deleted_at)
        self.assertIsNone(obj.deleted_by)
    
    def test_soft_delete(self):
        """Test de la suppression douce"""
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        obj.delete(user=self.user)
        
        self.assertTrue(obj.is_deleted)
        self.assertIsNotNone(obj.deleted_at)
        self.assertEqual(obj.deleted_by, self.user)
    
    def test_soft_delete_restore(self):
        """Test de la restauration"""
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        obj.delete(user=self.user)
        obj.restore()
        
        self.assertFalse(obj.is_deleted)
        self.assertIsNone(obj.deleted_at)
        self.assertIsNone(obj.deleted_by)
    
    def test_soft_delete_hard_delete(self):
        """Test de la suppression définitive"""
        class TestModel(SoftDeleteModel):
            name = models.CharField(max_length=100)
            
            class Meta:
                app_label = 'core'
        
        obj = TestModel.objects.create(name='Test')
        obj_id = obj.id
        obj.hard_delete()
        
        with self.assertRaises(TestModel.DoesNotExist):
            TestModel.objects.get(id=obj_id)

