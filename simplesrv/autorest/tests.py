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
        Person.objects.create(first_name="John", last_name="Travolta")

    def test_get_person_by_id(self):
        request = RequestFactory().get('/rest/person/')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)
        data = json.loads(response.content)
        self.assertEqual({"data": [{"id": 1, "first_name": "Lenny", "last_name": "Kravitz"}]}, data)

    def test_get_person_filtered_by_name(self):
        request = RequestFactory().get('/rest/person/?filter=[{"property":"first_name","operator":"eq","value":"John"}]')
        response = AnyModelRestView.as_view()(request, model_name='person')
        data = json.loads(response.content)
        self.assertEqual(
            {"data": [{"id": 2, "first_name": "John", "last_name": "Cena"},
                      {"id": 3, "first_name": "John", "last_name": "Travolta"}]}, data)

    def test_get_person_filtered_by_name_and_last_name(self):
        request = RequestFactory().get('/rest/person/?filter=[{"property":"first_name","operator":"eq","value":"John"}, {"property":"last_name","operator":"eq","value":"Cena"}]')
        response = AnyModelRestView.as_view()(request, model_name='person')
        data = json.loads(response.content)
        self.assertEqual({"data": [{"id": 2, "first_name": "John", "last_name": "Cena"}]}, data)

    def test_update_person_first_name(self):
        request = RequestFactory().put('/rest/person/1', {"first_name": "Lenny 1"}, content_type='application/json')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)

        request = RequestFactory().get('/rest/person/')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)
        data = json.loads(response.content)

        self.assertEqual({"data": [{"id": 1, "first_name": "Lenny 1", "last_name": "Kravitz"}]}, data)

    def test_create_new_person(self):
        request = RequestFactory().post('/rest/person/', [{"first_name": "Terry", "last_name": "Richardson"}], content_type='application/json')
        response = AnyModelRestView.as_view()(request, model_name='person')

        request = RequestFactory().get('/rest/person/?filter=[{"property":"first_name","operator":"eq","value":"Terry"}]')
        response = AnyModelRestView.as_view()(request, model_name='person')
        data = json.loads(response.content)
        self.assertEqual(
            {"data": [{"id": 4, "first_name": "Terry", "last_name": "Richardson"}]}, data)

    def test_delete_person(self):
        request = RequestFactory().delete('/rest/person/')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)

        request = RequestFactory().get('/rest/person/')
        response = AnyModelRestView.as_view()(request, model_name='person', id=1)
        data = json.loads(response.content)

        self.assertEqual({"data": []}, data)
