import pytest
from ddf import N

from core.models import Author




# G: Generador de datos
# N: Creador de instancias sin guardarlas en la bd
@pytest.fixture
def author_creation():
    return N(Author)


@pytest.mark.django_db 
def test_create_author(author_creation):
    print('author_creation: ', author_creation.name)
    author_creation.save()
    assert Author.objects.count() == 1








""" 
@pytest.mark.django_db
def test_common_user_creation():
    user = User.objects.create_user(
        username='dasdas',
        email='asdasda@gmail.com',
        nombres='wegw gwgwe',
        password='12345',
        is_staff=False
    )
    assert user.username == 'dasdas' 
"""

"""
@pytest.mark.django_db
def test_superuser_creation():
    user = User.objects.create_superuser(
        username='dasdas',
        email='asdasda@gmail.com',
        nombres='wegw gwgwe',
        password='12345'
    )
    assert user.is_superuser
"""

