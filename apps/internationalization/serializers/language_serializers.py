"""
Serializers pour les modèles de langue
"""
from rest_framework import serializers
from apps.internationalization.models import Language, LanguagePreference


class LanguageSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Language
    """
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Language
        fields = [
            'id', 'code', 'name', 'native_name', 'display_name',
            'is_active', 'is_default', 'is_rtl', 'flag_emoji',
            'country_code', 'region', 'auto_translate_enabled',
            'translation_quality', 'translation_count', 'last_used',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'translation_count', 'last_used']


class LanguagePreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle LanguagePreference
    """
    primary_language = LanguageSerializer(read_only=True)
    primary_language_code = serializers.CharField(write_only=True)
    secondary_languages = LanguageSerializer(many=True, read_only=True)
    secondary_language_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = LanguagePreference
        fields = [
            'id', 'primary_language', 'primary_language_code',
            'secondary_languages', 'secondary_language_codes',
            'auto_detect_language', 'show_original_text',
            'fallback_to_english', 'auto_translate_enabled',
            'translation_confidence_threshold', 'prefer_human_translation',
            'browser_language', 'timezone', 'last_updated',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_updated']
    
    def create(self, validated_data):
        """
        Crée une préférence de langue
        """
        primary_language_code = validated_data.pop('primary_language_code')
        secondary_language_codes = validated_data.pop('secondary_language_codes', [])
        
        try:
            primary_language = Language.objects.get(code=primary_language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue primaire "{primary_language_code}" non trouvée'
            )
        
        preference = LanguagePreference.objects.create(
            primary_language=primary_language,
            **validated_data
        )
        
        # Ajouter les langues secondaires
        for lang_code in secondary_language_codes:
            try:
                language = Language.objects.get(code=lang_code)
                preference.secondary_languages.add(language)
            except Language.DoesNotExist:
                raise serializers.ValidationError(
                    f'Langue secondaire "{lang_code}" non trouvée'
                )
        
        return preference
    
    def update(self, instance, validated_data):
        """
        Met à jour une préférence de langue
        """
        primary_language_code = validated_data.pop('primary_language_code', None)
        secondary_language_codes = validated_data.pop('secondary_language_codes', None)
        
        if primary_language_code:
            try:
                primary_language = Language.objects.get(code=primary_language_code)
                instance.primary_language = primary_language
            except Language.DoesNotExist:
                raise serializers.ValidationError(
                    f'Langue primaire "{primary_language_code}" non trouvée'
                )
        
        if secondary_language_codes is not None:
            instance.secondary_languages.clear()
            for lang_code in secondary_language_codes:
                try:
                    language = Language.objects.get(code=lang_code)
                    instance.secondary_languages.add(language)
                except Language.DoesNotExist:
                    raise serializers.ValidationError(
                        f'Langue secondaire "{lang_code}" non trouvée'
                    )
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class LanguageStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des langues
    """
    total_languages = serializers.IntegerField()
    default_language = LanguageSerializer()
    languages_with_translations = serializers.DictField()
    most_used_languages = serializers.ListField(
        child=serializers.DictField()
    )
    recent_languages = serializers.ListField(
        child=serializers.DictField()
    )

