from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from store.models import Book, UserBookRelationship


class BookReaderSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BooksSerializer(ModelSerializer):
    annotated_likes = serializers.IntegerField(read_only=True)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(source='owner.username', default='Anonymous', read_only=True)

    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'price', 'annotated_likes', 'rating', 'owner_name', 'readers')


class UserBookRelationshipSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelationship
        fields = ('book', 'like', 'bookmarks', 'rating')
