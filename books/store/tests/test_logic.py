from django.contrib.auth.models import User
from django.test import TestCase

from store.logic import set_rating
from store.models import Book, UserBookRelationship


class SetRatingTestCase(TestCase):
    def setUp(self) -> None:
        user1 = User.objects.create(username='user1',
                                    first_name='admin',
                                    last_name='admin')
        user2 = User.objects.create(username='user2',
                                    first_name='1',
                                    last_name='2'
                                    )
        user3 = User.objects.create(username='user3',
                                    first_name='3',
                                    last_name='4'
                                    )

        self.book_1 = Book.objects.create(title='worms', author='Me', price='1.00', owner=user1)

        UserBookRelationship.objects.create(user=user1, book=self.book_1, like=True,
                                            rating=5)
        UserBookRelationship.objects.create(user=user2, book=self.book_1, like=True,
                                            rating=4)
        UserBookRelationship.objects.create(user=user3, book=self.book_1, like=True,
                                            rating=5)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
