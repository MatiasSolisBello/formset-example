import pytest
from core.models import Author, Book
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

# Create your tests here.
"""
Todas las funciones que comienzan con "test_
@pytest.mark.django_db: indica a pytest que este test necesita acceso a bd
"""

@pytest.fixture
def formset_base():
    """
    Fixture que proporciona la estructura base de los datos de un formset.
    """
    return {
        'books-TOTAL_FORMS': '2',
        'books-INITIAL_FORMS': '0',
        'books-MIN_NUM_FORMS': '0',
        'books-MAX_NUM_FORMS': '1000',
    }

@pytest.fixture
def book_formset_class():
    """
    Fixture que proporciona la clase inlineformset_factory base para Author y Book.
    """
    return inlineformset_factory(Author, Book,
                                fields=('title', 'published_year'),
                                can_delete=True) 


# --- Tests ---

@pytest.mark.django_db 
def test_create_author():
    author = Author.objects.create(name="William Shakespeare")
    assert author.name == "William Shakespeare"
    

@pytest.mark.django_db 
def test_create_author_fail():    
    with pytest.raises(ValidationError):
        author = Author(name="")
        author.full_clean()
        
        
        
@pytest.mark.django_db
def test_author_book_inline_formset(formset_base, book_formset_class):
    
    # Creamos el autor
    author = Author.objects.create(name="Isaac Asimov")
    print('author: ', author)

    # Creamos el formset de libros asociados
    BookFormSet = inlineformset_factory(Author, Book, 
                                        fields=('title', 'published_year'), 
                                        extra=2, can_delete=True)
    
    data = formset_base.copy()
    data.update({
        'books-TOTAL_FORMS': '2',
        
        'books-0-title': 'Fundación',
        'books-0-published_year': '1951',
        
        'books-1-title': 'Yo, Robot',
        'books-1-published_year': '1950',
    })

    formset = BookFormSet(data=data, instance=author)
    assert formset.is_valid(), formset.errors

    # Guardamos los libros
    formset.save()

    assert Book.objects.filter(author=author).count() == 2
    assert set(Book.objects.values_list('title', flat=True)) == {'Fundación', 'Yo, Robot'}


@pytest.mark.django_db
def test_author_book_formset_edit_and_delete(formset_base, book_formset_class):
    # 1. Crear autor y libros iniciales
    author = Author.objects.create(name="Isaac Asimov")
    book1 = Book.objects.create(author=author, title="Fundación",
                                published_year=1951)
    book2 = Book.objects.create(author=author, title="Yo, Robot",
                                published_year=1950)

    # 2. Configurar el FormSet (2 iniciales, extra=1)
    BookFormSet = inlineformset_factory(
        Author, Book,
        fields=('title', 'published_year'),
        can_delete=True, extra=1
    )

    # 3. Simular el POST de edición, DELETE y creación a partir del fixture
    data = formset_base.copy()
    data.update({
        # 2 existentes + 1 nuevo
        'books-TOTAL_FORMS': '3',
        'books-INITIAL_FORMS': '2',

        # Libro 1 → lo editamos
        'books-0-id': str(book1.id),
        'books-0-title': 'Fundación (Edición Revisada)',
        'books-0-published_year': '1980',

        # Libro 2 → lo eliminamos
        'books-1-id': str(book2.id),
        'books-1-title': 'Yo, Robot',
        'books-1-published_year': '1950',
        'books-1-DELETE': 'on',  # clave para borrado

        # Libro nuevo
        'books-2-title': 'El Fin de la Eternidad',
        'books-2-published_year': '1955',
    })

    # 4. Procesar el formset
    formset = BookFormSet(data=data, instance=author)
    assert formset.is_valid(), formset.errors

    formset.save()

    # 5. Verificaciones
    libros = Book.objects.filter(author=author)
    titulos = set(libros.values_list('title', flat=True))

    assert libros.count() == 2
    assert 'Fundación (Edición Revisada)' in titulos
    assert 'El Fin de la Eternidad' in titulos
    assert 'Yo, Robot' not in titulos


@pytest.mark.django_db
def test_empty_form_is_ignored(formset_base, book_formset_class):
    author = Author.objects.create(name="Isaac Asimov")

    BookFormSet = inlineformset_factory(
        Author, Book,
        fields=('title', 'published_year'),
        extra=1 # Para tener un formulario vacío
    )

    # Preparamos los datos a partir del fixture base
    data = formset_base.copy()
    data.update({
        'books-TOTAL_FORMS': '1', # Solo el formulario extra
        'books-0-title': '',
        'books-0-published_year': '',
    })

    formset = BookFormSet(data=data, instance=author)
    assert formset.is_valid(), formset.errors
    assert formset.total_form_count() == 1
    # no crea ningún libro porque es un formulario extra vacío
    assert len(formset.save(commit=False)) == 0


@pytest.mark.django_db
def test_invalid_book_formset(formset_base, book_formset_class):
    author = Author.objects.create(name="Asimov")
    BookFormSet = book_formset_class # Usamos la clase base (extra=0, can_delete=True)

    # Preparamos los datos a partir del fixture base
    data = formset_base.copy()
    data.update({
        'books-TOTAL_FORMS': '1',
        'books-0-title': '', # Inválido si 'title' es requerido
        'books-0-published_year': '1950',
    })

    formset = BookFormSet(data=data, instance=author)
    assert not formset.is_valid()
    assert 'title' in formset.errors[0]


@pytest.mark.django_db
def test_books_linked_to_correct_author():
    author1 = Author.objects.create(name="Asimov")
    author2 = Author.objects.create(name="Clarke")

    Book.objects.create(author=author1, title="Fundación", published_year=1951)
    assert Book.objects.filter(author=author2).count() == 0


@pytest.mark.django_db
def test_formset_save_commit_false(formset_base, book_formset_class):
    author = Author.objects.create(name="Asimov")
    # Configurar el FormSet específico para la creación (extra=1)
    BookFormSet = inlineformset_factory(Author, Book, fields=('title', 'published_year'), extra=1)

    # Preparamos los datos a partir del fixture base
    data = formset_base.copy()
    data.update({
        'books-TOTAL_FORMS': '1',
        'books-0-title': 'Nueva Fundación',
        'books-0-published_year': '1982',
    })

    formset = BookFormSet(data=data, instance=author)
    assert formset.is_valid()
    unsaved_books = formset.save(commit=False)
    assert len(unsaved_books) == 1
    assert Book.objects.filter(author=author).count() == 0  # aún no guardados