from django.contrib import admin
from store.models import Book, UserBookRelationship


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(UserBookRelationship)
class UserBookRelationshipAdmin(admin.ModelAdmin):
    pass
