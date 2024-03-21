from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    objects = None
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, through='UserBookRelationship', related_name='read_books')  # through — through which model of relation

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)

    def __str__(self):
        return self.title


class UserBookRelationship(models.Model):
    RATE_CHOICES = (
        (1, 'Horrible'),
        (2, 'Bad'),
        (3, 'Ok'),
        (4, 'Good'),
        (5, 'Amazing')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    like = models.BooleanField(default=False)
    bookmarks = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f'{self.user.username}: {self.book.title}, RATE: {self.rating}'

    def save(self, *args, **kwargs):
        from store.logic import set_rating

        creating = not self.pk
        old_rating = self.rating

        super().save(*args, **kwargs)

        new_rating = self.rating
        if old_rating != new_rating or creating:
            set_rating(self.book)
