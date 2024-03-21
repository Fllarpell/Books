from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelationship
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
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

        book_1 = Book.objects.create(title='worms', author='Me', price='1.00', owner=user1)
        book_2 = Book.objects.create(title='biology', author='NotMe', price='2.00', owner=user2)

        UserBookRelationship.objects.create(user=user1, book=book_1, like=True,
                                            rating=5)
        UserBookRelationship.objects.create(user=user2, book=book_1, like=True,
                                            rating=4)
        UserBookRelationship.objects.create(user=user3, book=book_1, like=True,
                                            rating=5)


        UserBookRelationship.objects.create(user=user1, book=book_2, like=True,
                                            rating=3)
        UserBookRelationship.objects.create(user=user2, book=book_2, like=True,
                                            rating=4)
        UserBookRelationship.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelationship__like=True, then=1)))
        ).order_by('id')

        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'title': 'worms',
                'author': 'Me',
                'price': '1.00',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'user1',
                'readers': [
                    {
                        'first_name': 'admin',
                        'last_name': 'admin'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    },
                    {
                        'first_name': '3',
                        'last_name': '4'
                    },

                ]
            },
            {
                'id': book_2.id,
                'title': 'biology',
                'author': 'NotMe',
                'price': '2.00',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': 'user2',
                'readers': [
                    {
                        'first_name': 'admin',
                        'last_name': 'admin'
                    },
                    {
                        'first_name': '1',
                        'last_name': '2'
                    },
                    {
                        'first_name': '3',
                        'last_name': '4'
                    },
                ]
            },
        ]

        self.assertEqual(expected_data, data)
