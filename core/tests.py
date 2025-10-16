import pytest
from core.models import Author, Book

# Create your tests here.
"""
Todas las funciones que comienzan con "test_
@pytest.mark.django_db: indica a pytest que este test necesita acceso a bd
"""

@pytest.mark.django_db
def test_get_author():
    author = Author.objects.get(name='Stephen King')
    assert author.name == "Stephen King"
    
    
@pytest.mark.django_db 
def test_create_author():
    author = Author.objects.create(name="Test Author")
    assert author.name == "Test Author"
    
   
