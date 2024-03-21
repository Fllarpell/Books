from django.db.models import Avg

from store.models import UserBookRelationship


def set_rating(book):
    rating = UserBookRelationship.objects.filter(book=book).aggregate(rate=Avg('rating')).get('rate')
    book.rating = rating
    book.save()
