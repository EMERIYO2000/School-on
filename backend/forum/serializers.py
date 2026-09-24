from rest_framework import serializers

from .models import ForumPost, ForumThread


class ForumPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = ('id', 'author', 'content', 'created_at', 'is_accepted_solution')
        read_only_fields = ('id', 'author', 'created_at', 'is_accepted_solution')

    def get_author(self, obj):
        return {
            'id': obj.author_id,
            'full_name': obj.author.get_full_name() or obj.author.username,
            'email': obj.author.email,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
        }


class ForumThreadSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.name', read_only=True)
    replies_count = serializers.IntegerField(source='posts.count', read_only=True)
    replies = ForumPostSerializer(many=True, read_only=True)

    class Meta:
        model = ForumThread
        fields = ('id', 'title', 'content', 'author', 'category', 'created_at', 'is_closed', 'replies_count', 'replies')
        read_only_fields = ('id', 'author', 'category', 'created_at', 'is_closed', 'replies_count', 'replies')

    def get_author(self, obj):
        return {
            'id': obj.author_id,
            'full_name': obj.author.get_full_name() or obj.author.username,
            'email': obj.author.email,
            'avatar': obj.author.avatar.url if obj.author.avatar else None,
        }


class CreateForumThreadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    content = serializers.CharField()
    category = serializers.CharField(required=False, allow_blank=True)


class CreateForumPostSerializer(serializers.Serializer):
    content = serializers.CharField()
