import json

from django.test import RequestFactory, TestCase
from django.urls import resolve
from django.http import HttpRequest

from .models import Person
from .views import AnyModelRestView


class AnyModelRestViewTestCase(TestCase):

    def setUp(self):
        Person.objects.create(first_name="Lenny", last_name="Kravitz")
        Person.objects.create(first_name="John", last_name="Cena")

    def test_get_person_by_id(self):
        request = RequestFactory().get('/rest/person/')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)
        data = json.loads(response.content)
        self.assertEqual({"data": [{"id": 1, "first_name": "Lenny", "last_name": "Kravitz"}]}, data)

