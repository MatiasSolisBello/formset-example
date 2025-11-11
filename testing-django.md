# Índice

- [Instalación de pytest](#instalación-de-pytest)
- [Fixture y Raises](#fixture-y-raises)
- [Faker](#faker)
  - [Crear provider personalizado](#crear-provider-personalizado)
- [Dynamic Fixture](#dynamic-fixture)
- [Conftest y Factory Boy](#conftest-y-factory-boy)
- [TestCase](#testcase)
- [Client](#client)

---

# Instalación de pytest

[Documentación de pytest-django](https://pytest-django.readthedocs.io/en/latest/ "Documentación de pytest-django")
```shell
pip install pytest-django
```

Es recomendable usar multiples test.py por motivos de escalabilidad del sistema. Es recomendable, en la raiz del proyecto, tener una carpeta **tests** y configurarlo:

pytest.ini
```python
[pytest]

# cargar settings.py: MODIFICAR project_name
DJANGO_SETTINGS_MODULE = project_name.settings

python_files = tests.py tests_*.py *_tests.py

# opcional, acelera pruebas reusando la base de datos y saltando migraciones
addopts = --reuse-db --nomigrations
```

tests/test_user.py
```python
import pytest
from core.models import Usuario

# Las funciones siempre deben empezar con "test_"
@pytest.mark.django_db 
def test_user_creation():
	user = Usuario.objects.create_user(
		username='user1', email='user1@email.com', password='123'
	)
	assert user.username == 'user1'


@pytest.mark.django_db
def test_common_user_creation():
    user = User.objects.create_user(
        username='dasdas',
        email='asdasda@gmail.com',
        nombres='wegw gwgwe',
        password='12345',
        is_staff=True
    )
    assert user.is_staff


@pytest.mark.django_db
def test_superuser_creation():
    user = User.objects.create_superuser(
        username='dasdas',
        email='asdasda@gmail.com',
        nombres='wegw gwgwe',
        password='12345'
    )
    assert user.is_superuser

```

[Leer documentacion de assert en testing con python](https://ellibrodepython.com/python-testing "Leer documentacion de assert en testing con python")

Ejecutar:
```shell
pytest
```


# Fixture y Raises

Raises: Comprobar excepciones

```python
@pytest.mark.django_db
def test_user_creation_fail():
	with pytest.raises(Exception):  
		Usuario.objects.create_user(
			password='12345',
			is_staff=False
		)
```
[Leer documentación de excepciones en asserts](https://docs.pytest.org/en/6.2.x/assert.html#assertions-about-expected-exceptions "Leer documentación de excepciones en asserts")

Fixture: Recibir una funcion como parametro

```python
@pytest.fixture
def user_creation():
	return Usuario(
		username='kjbkwejfw',
		email='asdasd@gmail.com',
		nombres='sadasd fasfas',
		password='12345'
	)

@pytest.mark.django_db
def test_common_user_creation(user_creation):
	user_creation.is_staff = False
	user_creation.save()
	assert user_creation.is_staff == False
```

# Faker
Creación de información falsa para pruebas

```shell
pip install faker
```

```python
from faker import Faker

fake = Faker()

@pytest.fixture
def user_creation():
	return Usuario(
		username=fake.first_name(), # estas funciones se llaman providers
		email=fake.email(),
		nombres=fake.name(),
		password=fake.password()
	)
```
[Leer otros ejemplos de providers](https://faker.readthedocs.io/en/master/providers.html "Leer otros ejemplos de providers")

## Crear provider personalizado

tests/providers/general_providers.py
```python
from faker import Faker
from faker.providers import BaseProvider

fake = Faker()

class EmailProvider(BaseProvider):
  def custom_email(self):
      return f'{fake.last_name().lower()}@gmail.com' 
```

tests/test_user.py
```python
from faker import Faker
from tests.providers.general_providers import EmailProvider


fake = Faker()
fake.add_provider(EmailProvider) # <- Clase personalizada 

@pytest.fixture
def user_creation():
	return Usuario(
		# ...
		email=fake.custom_email(), # <- Metodo personalizado
	)
```

# Dynamic Fixture
Crear instancias de modelos dinámicos

* Este colocara None cuando el campo no es obligatorio
* El id (AutoField) se completa automáticamente, a menos que le establezca un valor.
* Si un campo tiene valor predeterminado, se utiliza de forma predeterminada
* Si un campo tiene opciones, la primera opción está seleccionada de forma predeterminada.

```shell
pip install django-dynamic-fixture
```
[Leer documentación oficial]([https://faker.readthedocs.io/en/master/providers.html](https://django-dynamic-fixture.readthedocs.io/en/latest/index.html) "Leer documentación oficial")

## Uso de G:

Recibe una clase del models.py y devolverá una instancia válida y persistente Lleno de datos generados dinámicamente

```python
from ddf import G

@pytest.fixture
def user_creation():
    return G(Usuario)
```

## Uso de N:
La funcion N es similar a G, excepto que NO guardará la instancia generada. Esto es bueno para pruebas unitarias, sin tocar la base de datos

También se puede utilizar para manipule la instancia antes de guardarla. Por lo general, lo necesitamos para trabajar con campos personalizados, validaciones personalizadas, etc. Para estos casos, podemos usar el persist_dependencies=True parámetro para guardar dependencias internas de campos ForeignKey y OneToOneField 

```python
book = N(Book, persist_dependencies=True)
assert book.id is None # the Book was not persisted
assert book.publisher.id is not None # internal dependency was persisted
```
Dado que la instancia no tiene un ID, NO puede insertar instancias en campos ManyToManyField. Por lo tanto, tenga cuidado de utilizar el G función para estos casos.

## Uso de F 

Personalizar recursivamente a través de campos de relación ForeignKey, OneToOneField y ManyToManyField

```python
from ddf import G, N, F

@pytest.fixture
def user_creation():
    rol = G(Rol)
    return N(Usuario, rol=rol)
```

## DDF con ManyToMany

Ejemplo (models.py)
```python
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=255)

class Book(models.Model):
    name = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author)

    @staticmethod
    def search_by_author(author_name):
        return Book.objects.filter(authors__name=author_name)
```

PyTest ejemplo (tests/test_books.py)
```python
from django.test import TestCase
from ddf import G

def test_search_book_by_author():
    author1 = G(Author)
    author2 = G(Author)

    book1 = G(Book, authors=[author1])
    book2 = G(Book, authors=[author2])

    books = Book.objects.search_by_author(author1.name)
    assert book1 in books
    assert book2 not in books
```

Django TestCase (tests/test_books.py)
```python
from django.test import TestCase
from ddf import G

class SearchingBooks(TestCase):
    def test_search_book_by_author(self):
        author1 = G(Author)
        author2 = G(Author)

        book1 = G(Book, authors=[author1])
        book2 = G(Book, authors=[author2])

        books = Book.objects.search_by_author(author1.name)
        self.assertTrue(book1 in books)
        self.assertTrue(book2 not in books)
```

## Uso de M

característica que le indica a DDF que genere una cadena aleatoria usando una "máscara" (por eso se llama M o Mask) personalizada

* #: representa un número: 0-9
* -: representa un carácter mayúscula: AZ
* _: representa un carácter minúsculo: az
* !: símbolos de máscara de escape, incluido él mismo

```python
from ddf import G, M
instance = G(Publisher, address=M(r'St. -______, ### !- -- --'))
assert instance.address == 'St. Imaiden, 164 - SP BR'
```

## Uso de C

Función para copiar los datos de un campo a otro

```python
from ddf import G, C

user = G(User, first_name=C('username'))
assert instance.first_name == instance.username

instance = G(MyModel, first_name=C('username'), username='eistein')
assert instance.first_name == 'eistein'
```

# Conftest

Es un archivo especial (conftest.py) que define fixtures que se compartirán entre todas las pruebas de ese paquete y sus subdirectorios.

Entre sus ventajas esta la reutilización, organización y simplificación

conftest.py
```python
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from app.models import Post


@pytest.fixture
def api_client():
    """Cliente DRF para hacer peticiones HTTP."""
    return APIClient()


@pytest.fixture
def user(db):
    """Crea un usuario de prueba."""
    return User.objects.create_user(username="tester", password="1234")


@pytest.fixture
def auth_client(api_client, user):
    """Devuelve un cliente autenticado."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def post(db, user):
    """Crea un post de prueba."""
    return Post.objects.create(title="Post de prueba", author=user, content="Texto de ejemplo")
```

Ejemplo de uso en test_views.py
```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_list_posts(auth_client, post):
    url = reverse("posts-list")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) >= 1
    assert response.data[0]["title"] == "Post de prueba"

```
Así evitas repetir el mismo User.objects.create() o APIClient() en cada test.


# Factory Boy

Es una librería que reemplaza los fixtures estáticos con factories: clases que generan objetos de prueba bajo demanda, con datos realistas y personalizables. Es decir, en lugar de tener una función que “crea un usuario”, defines una fábrica de usuarios que puede crear cientos de usuarios distintos sin repetir código.

**Ventajas frente a fixtures tradicionales**
* Menos repetición: defines la estructura una vez, luego puedes modificar solo los campos que necesitas.
* Más control: puedes crear objetos válidos y consistentes sin preocuparte por dependencias (por ejemplo, un Post que siempre tenga un User válido).
* Escalable: ideal cuando tu modelo crece o tiene relaciones complejas.

```shell
pip install factory_boy
```
[Documentacion Factory Boy](https://factoryboy.readthedocs.io/en/stable/index.html "Documentacion Factory Boy")


factories.py
```python
import factory
from django.contrib.auth.models import User
from app.models import Post


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@test.com")
    password = factory.PostGenerationMethodCall("set_password", "1234")


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    content = factory.Faker("paragraph")
    author = factory.SubFactory(UserFactory)
```

conftest.py
```python
import pytest
from rest_framework.test import APIClient
from pytest_factoryboy import register
from .factories import UserFactory, PostFactory

# Registramos las factories como fixtures de pytest
register(UserFactory)
register(PostFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user_factory):
    """Cliente autenticado con un usuario generado por factory."""
    user = user_factory()
    api_client.force_authenticate(user=user)
    return api_client
```

test_views.py
```python
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_list_posts(auth_client, post_factory):
    # Creamos varios posts fácilmente
    post_factory.create_batch(3)
    url = reverse("posts-list")
    response = auth_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3

```


# TestCase

Ejemplo con modelo Post con title, content, author(FK, User)
```python
from django.test import TestCase
from .factories import PostFactory

class PostModelTest(TestCase):
    def setUp(self):
        self.post = PostFactory(title="Título fijo de prueba")

    def test_post_creation(self):
        self.assertIsNotNone(self.post.id)
        self.assertEqual(self.post.title, "Título fijo de prueba")
        self.assertTrue(self.post.author.username.startswith("user_"))
```

[Documentacion Django Testing](https://docs.djangoproject.com/en/5.2/topics/testing/overview/ "Documentacion Django Testing")


# Client

Ejemplo con modelo Post con title, content, author(FK, User)

```python
from django.test import TestCase, Client
from django.urls import reverse
from .factories import UserFactory, PostFactory

class PostViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.user.set_password("1234")
        self.user.save()

        self.post = PostFactory(author=self.user)

    def test_list_posts(self):
        url = reverse("posts-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_create_post_authenticated(self):
        self.client.login(username=self.user.username, password="1234")
        url = reverse("posts-list")
        data = {"title": "Nuevo post", "content": "Texto nuevo", "author": self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # redirección tras crear, por ejemplo
        self.assertTrue(self.user.post_set.filter(title="Nuevo post").exists())
```
**Qué pasa detrás**
* Client() crea un cliente HTTP interno que usa la misma lógica que Django al procesar peticiones, pero sin levantar el servidor.
* 'self.client.get()', 'post()', 'put()', etc., simulan requests reales.
* self.client.login() maneja autenticación con la sesión del test (útil para vistas con @login_required).
* La BD se crea y destruye automáticamente por TestCase.
