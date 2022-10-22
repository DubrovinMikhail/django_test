import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from model_bakery import baker


URL = 'http://127.0.0.1:8000/api/v1'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.mark.django_db  # тест успешного создания через фабрику
def test_create_course(client, course_factory):
    course = course_factory()
    resp = client.get(f'{URL}/courses/{course.id}/')
    assert resp.status_code == 200
    assert resp.data['name'] == course.name


@pytest.mark.django_db  # проверка получения списка курсов
def test_get_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(f'{URL}/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)
    for i, course in enumerate(data):
        assert course['name'] == courses[i].name


@pytest.mark.django_db  # проверка фильтрации списка курсов по id
def test_get_filter_id_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    courses_ids = [i.id for i in courses]
    for course_id in courses_ids:
        resp = client.get(f'{URL}/courses/?id={course_id}')
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]['id'] == course_id


@pytest.mark.django_db  # проверка фильтрации списка курсов по name
def test_get_filter_id_courses(client, course_factory):
    courses = course_factory(_quantity=10)
    courses_name = [i.name for i in courses]
    for course_name in courses_name:
        resp = client.get(f'{URL}/courses/?name={course_name}')
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]['name'] == course_name


@pytest.mark.django_db   # тест успешного создания курса через API
def test_create_course_api(client):
    course = {'name': 'Python'}
    resp = client.post(f'{URL}/courses/', course)
    assert resp.status_code == 201
    resp2 = client.get(f'{URL}/courses/{resp.data["id"]}/')
    assert resp2.status_code == 200
    assert resp2.data['name'] == course['name']


@pytest.mark.django_db  # тест успешного обновления
def test_update_course(client, course_factory):
    course = course_factory()
    new_name = 'django'
    resp = client.get(f'{URL}/courses/')
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['name'] == course.name
    resp2 = client.patch(f'{URL}/courses/{course.id}/', {'name': new_name})
    assert resp2.status_code == 200
    resp3 = client.get(f'{URL}/courses/')
    data = resp3.json()
    assert data[0]['name'] == new_name


@pytest.mark.django_db  # тест успешного удаления
def test_delete_course(client, course_factory):
    course = course_factory()
    resp = client.get(f'{URL}/courses/')
    assert resp.status_code == 200
    resp2 = client.delete(f'{URL}/courses/{course.id}/')
    assert resp2.status_code == 204
    resp3 = client.get(f'{URL}/courses/{course.id}/')
    assert resp3.status_code == 404
