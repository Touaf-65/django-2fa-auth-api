"""
Modèles pour la gestion des langues
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import TimestampedModel

User = get_user_model()


class Language(TimestampedModel):
    """Langue supportée par l'application"""
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'Français'),
        ('es', 'Español'),
        ('de', 'Deutsch'),
        ('it', 'Italiano'),
        ('pt', 'Português'),
        ('ru', 'Русский'),
        ('zh', '中文'),
        ('ja', '日本語'),
        ('ko', '한국어'),
        ('ar', 'العربية'),
        ('hi', 'हिन्दी'),
        ('th', 'ไทย'),
        ('vi', 'Tiếng Việt'),
        ('tr', 'Türkçe'),
        ('pl', 'Polski'),
        ('nl', 'Nederlands'),
        ('sv', 'Svenska'),
        ('da', 'Dansk'),
        ('no', 'Norsk'),
        ('fi', 'Suomi'),
        ('cs', 'Čeština'),
        ('hu', 'Magyar'),
        ('ro', 'Română'),
        ('bg', 'Български'),
        ('hr', 'Hrvatski'),
        ('sk', 'Slovenčina'),
        ('sl', 'Slovenščina'),
        ('et', 'Eesti'),
        ('lv', 'Latviešu'),
        ('lt', 'Lietuvių'),
        ('mt', 'Malti'),
        ('cy', 'Cymraeg'),
        ('ga', 'Gaeilge'),
        ('eu', 'Euskera'),
        ('ca', 'Català'),
        ('gl', 'Galego'),
    ]
    
    code = models.CharField(max_length=5, unique=True, choices=LANGUAGE_CHOICES)
    name = models.CharField(max_length=100)
    native_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    is_rtl = models.BooleanField(default=False)  # Right-to-left
    
    # Métadonnées
    flag_emoji = models.CharField(max_length=10, blank=True)
    country_code = models.CharField(max_length=2, blank=True)
    region = models.CharField(max_length=50, blank=True)
    
    # Configuration de traduction automatique
    auto_translate_enabled = models.BooleanField(default=True)
    translation_quality = models.CharField(
        max_length=20,
        choices=[
            ('high', 'Haute'),
            ('medium', 'Moyenne'),
            ('low', 'Faible'),
        ],
        default='medium'
    )
    
    # Statistiques
    translation_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Langue"
        verbose_name_plural = "Langues"
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une seule langue est par défaut
        if self.is_default:
            Language.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        """Nom d'affichage avec emoji"""
        if self.flag_emoji:
            return f"{self.flag_emoji} {self.native_name}"
        return self.native_name


class LanguagePreference(TimestampedModel):
    """Préférences de langue des utilisateurs"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='language_preference')
    primary_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='primary_users')
    secondary_languages = models.ManyToManyField(Language, blank=True, related_name='secondary_users')
    
    # Préférences d'affichage
    auto_detect_language = models.BooleanField(default=True)
    show_original_text = models.BooleanField(default=False)
    fallback_to_english = models.BooleanField(default=True)
    
    # Préférences de traduction
    auto_translate_enabled = models.BooleanField(default=True)
    translation_confidence_threshold = models.FloatField(default=0.8)
    prefer_human_translation = models.BooleanField(default=True)
    
    # Métadonnées
    browser_language = models.CharField(max_length=10, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Préférence de Langue"
        verbose_name_plural = "Préférences de Langue"
    
    def __str__(self):
        return f"{self.user.username} - {self.primary_language.name}"
    
    def get_available_languages(self):
        """Retourne toutes les langues disponibles pour l'utilisateur"""
        languages = [self.primary_language]
        languages.extend(self.secondary_languages.all())
        return languages
    
    def get_preferred_language(self, available_languages=None):
        """Retourne la langue préférée parmi celles disponibles"""
        if available_languages is None:
            return self.primary_language
        
        # Vérifier la langue primaire
        if self.primary_language in available_languages:
            return self.primary_language
        
        # Vérifier les langues secondaires
        for lang in self.secondary_languages.all():
            if lang in available_languages:
                return lang
        
        # Fallback vers l'anglais si activé
        if self.fallback_to_english:
            try:
                english = Language.objects.get(code='en')
                if english in available_languages:
                    return english
            except Language.DoesNotExist:
                pass
        
        # Retourner la première langue disponible
        return available_languages[0] if available_languages else None

