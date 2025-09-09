"""
Serializers pour les modèles de traduction
"""
from rest_framework import serializers
from apps.internationalization.models import TranslationKey, Translation, TranslationRequest


class TranslationKeySerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle TranslationKey
    """
    source_language = serializers.StringRelatedField(read_only=True)
    source_language_code = serializers.CharField(write_only=True)
    
    class Meta:
        model = TranslationKey
        fields = [
            'id', 'key', 'context', 'source_text', 'source_language',
            'source_language_code', 'description', 'tags', 'is_active',
            'priority', 'usage_count', 'last_used', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'usage_count', 'last_used']
    
    def create(self, validated_data):
        """
        Crée une clé de traduction
        """
        from apps.internationalization.models import Language
        
        source_language_code = validated_data.pop('source_language_code')
        try:
            source_language = Language.objects.get(code=source_language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue source "{source_language_code}" non trouvée'
            )
        
        return TranslationKey.objects.create(
            source_language=source_language,
            **validated_data
        )


class TranslationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Translation
    """
    translation_key = TranslationKeySerializer(read_only=True)
    language = serializers.StringRelatedField(read_only=True)
    language_code = serializers.CharField(write_only=True)
    translated_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Translation
        fields = [
            'id', 'translation_key', 'language', 'language_code',
            'translated_text', 'status', 'confidence_score',
            'translation_service', 'translated_by', 'reviewed_by',
            'translated_at', 'reviewed_at', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'translated_at', 'reviewed_at'
        ]
    
    def create(self, validated_data):
        """
        Crée une traduction
        """
        from apps.internationalization.models import Language
        
        language_code = validated_data.pop('language_code')
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue "{language_code}" non trouvée'
            )
        
        return Translation.objects.create(
            language=language,
            **validated_data
        )


class TranslationRequestSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle TranslationRequest
    """
    source_language = serializers.StringRelatedField(read_only=True)
    source_language_code = serializers.CharField(write_only=True)
    target_languages = serializers.StringRelatedField(many=True, read_only=True)
    target_language_codes = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    requested_by = serializers.StringRelatedField(read_only=True)
    completed_translations = TranslationSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = TranslationRequest
        fields = [
            'id', 'source_text', 'source_language', 'source_language_code',
            'target_languages', 'target_language_codes', 'context', 'priority',
            'status', 'requested_by', 'use_auto_translation',
            'require_human_review', 'translation_service',
            'completed_translations', 'error_message', 'started_at',
            'completed_at', 'progress_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'started_at', 'completed_at',
            'error_message', 'completed_translations'
        ]
    
    def create(self, validated_data):
        """
        Crée une demande de traduction
        """
        from apps.internationalization.models import Language
        
        source_language_code = validated_data.pop('source_language_code')
        target_language_codes = validated_data.pop('target_language_codes')
        
        try:
            source_language = Language.objects.get(code=source_language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue source "{source_language_code}" non trouvée'
            )
        
        target_languages = []
        for lang_code in target_language_codes:
            try:
                language = Language.objects.get(code=lang_code)
                target_languages.append(language)
            except Language.DoesNotExist:
                raise serializers.ValidationError(
                    f'Langue cible "{lang_code}" non trouvée'
                )
        
        request = TranslationRequest.objects.create(
            source_language=source_language,
            **validated_data
        )
        
        request.target_languages.set(target_languages)
        return request


class TranslationStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques de traduction
    """
    total_translations = serializers.IntegerField()
    auto_translated = serializers.IntegerField()
    human_translated = serializers.IntegerField()
    reviewed = serializers.IntegerField()
    approved = serializers.IntegerField()
    pending = serializers.IntegerField()
    rejected = serializers.IntegerField()
    auto_translation_percentage = serializers.FloatField()

