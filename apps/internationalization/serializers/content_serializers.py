"""
Serializers pour les modèles de contenu
"""
from rest_framework import serializers
from apps.internationalization.models import Content, ContentTranslation


class ContentSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Content
    """
    source_language = serializers.StringRelatedField(read_only=True)
    source_language_code = serializers.CharField(write_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    available_languages = serializers.ReadOnlyField()
    
    class Meta:
        model = Content
        fields = [
            'id', 'content_type', 'identifier', 'title', 'description',
            'source_language', 'source_language_code', 'tags', 'is_active',
            'is_public', 'created_by', 'available_languages',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'available_languages']
    
    def create(self, validated_data):
        """
        Crée un contenu
        """
        from apps.internationalization.models import Language
        
        source_language_code = validated_data.pop('source_language_code')
        try:
            source_language = Language.objects.get(code=source_language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue source "{source_language_code}" non trouvée'
            )
        
        return Content.objects.create(
            source_language=source_language,
            **validated_data
        )


class ContentTranslationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle ContentTranslation
    """
    content = ContentSerializer(read_only=True)
    language = serializers.StringRelatedField(read_only=True)
    language_code = serializers.CharField(write_only=True)
    translated_by = serializers.StringRelatedField(read_only=True)
    reviewed_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ContentTranslation
        fields = [
            'id', 'content', 'language', 'language_code',
            'translated_title', 'translated_description', 'translated_content',
            'status', 'is_active', 'translated_by', 'reviewed_by',
            'translated_at', 'reviewed_at', 'published_at',
            'translation_quality', 'notes', 'meta_title',
            'meta_description', 'meta_keywords', 'slug',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'translated_at',
            'reviewed_at', 'published_at', 'slug'
        ]
    
    def create(self, validated_data):
        """
        Crée une traduction de contenu
        """
        from apps.internationalization.models import Language
        
        language_code = validated_data.pop('language_code')
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            raise serializers.ValidationError(
                f'Langue "{language_code}" non trouvée'
            )
        
        return ContentTranslation.objects.create(
            language=language,
            **validated_data
        )


class ContentSearchSerializer(serializers.Serializer):
    """
    Serializer pour les résultats de recherche de contenu
    """
    content = ContentSerializer()
    match_type = serializers.CharField()
    language = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    translation = ContentTranslationSerializer(required=False)

