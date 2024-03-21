import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelationship
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.url = reverse('book-list')

        self.user = User.objects.create(username='test_username')

        self.book_1 = Book.objects.create(title='Test book 1 Ya', author='hui',
                                          price='1.00', owner=self.user)
        self.book_2 = Book.objects.create(title='Test book 2', author='hz',
                                          price='55.01', owner=self.user)
        self.book_3 = Book.objects.create(title='Test book 3', author='Ya',
                                          price='2.02', owner=self.user)

    def test_get(self):
        response = self.client.get(self.url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelationship__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        data = {
            "title": "Programming in Python 3",
            "author": "Mark Summerfield",
            "price": "150.00"
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        self.url = reverse('book-detail', args=(self.book_1.id, ))
        data = {
            "title": self.book_1.title,
            "author": self.book_1.author,
            "price": 575
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_delete(self):
        self.url = reverse('book-detail', args=(self.book_1.id,))

        self.client.force_login(self.user)
        response = self.client.delete(self.url, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_not_owner(self):
        self.url = reverse('book-detail', args=(self.book_1.id, ))
        self.user2 = User.objects.create(username='test_username2')
        data = {
            "title": self.book_1.title,
            "author": self.book_1.author,
            "price": 575
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book_1.refresh_from_db()
        self.assertEqual(1, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.url = reverse('book-detail', args=(self.book_1.id, ))
        self.user2 = User.objects.create(username='test_username2', is_staff=True)
        data = {
            "title": self.book_1.title,
            "author": self.book_1.author,
            "price": 575
        }

        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_1.refresh_from_db()
        self.assertEqual(575, self.book_1.price)

    def test_get_filter(self):
        response = self.client.get(self.url, data={'price': '55.01'})
        books = Book.objects.filter(id__in=[self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelationship__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        response = self.client.get(self.url, data={'search': 'Ya'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelationship__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        response = self.client.get(self.url, data={'ordering': 'price'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id, self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelationship__like=True, then=1)))
        )
        serializer_data = BooksSerializer(books, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer_data, response.data)


class BooksRelationTestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')

        self.book_1 = Book.objects.create(title='Test book 1 Ya', author='hui',
                                          price='1.00', owner=self.user)
        self.book_2 = Book.objects.create(title='Test book 2', author='hz',
                                          price='55.01', owner=self.user)
        self.book_3 = Book.objects.create(title='Test book 3', author='Ya',
                                          price='2.02', owner=self.user)

    def test_like(self):
        self.url = reverse('userbookrelationship-detail', args=(self.book_1.id, ))

        data = {
            "like": True,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelationship.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

        data = {
            "bookmarks": True,
        }
        json_data = json.dumps(data)

        response = self.client.patch(self.url, data=json_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelationship.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.bookmarks)

    def test_bookmarks(self):
        self.url = reverse('userbookrelationship-detail', args=(self.book_1.id, ))

        data = {
            "bookmarks": True,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelationship.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.bookmarks)

    def test_rating(self):
        self.url = reverse('userbookrelationship-detail', args=(self.book_1.id, ))

        data = {
            "rating": 3,
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(self.url, data=json_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        relation = UserBookRelationship.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(3, relation.rating)
