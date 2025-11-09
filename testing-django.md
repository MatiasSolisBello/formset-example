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
Crear instancias automaticamente

* este colocara None cuando el campo no es obligatorio

```shell
pip install django-dynamic-fixture
```

Uso de G:
```python
from ddf import G

@pytest.fixture
def user_creation():
    return G(Usuario)
```

Con llaves foraneas.
```python
from ddf import G, N, F

@pytest.fixture
def user_creation():
    rol = G(Rol)
    return N(Usuario, rol=rol)
```

DDF con ManyToMany
```python
import pytest

from faker import Faker
from ddf import G, F

from apps.libro.models import Autor, Libro

fake = Faker()

@pytest.fixture
def create_libro():
    # forma 1
    autor_1 = G(Autor, )
    autor_2 = G(Autor)
    return G(Libro, autor=[autor_1, autor_2, F()])

    # forma 2
    # autores = [F(nombre=fake.last_name()), F(nombre=fake.first_name())]

    # forma 3
    # return G(Libro, autor=[F(nombre=fake.last_name()), F(nombre=fake.first_name())])

@pytest.mark.django_db
def test_create_libro(create_libro):
    print(create_libro.autor.all())
    assert create_libro.estado
```

# Conftest y Factory Boy
Conftest: 

Factory Boy: Definir archivos tipo "modelos" para el test

[Documentacion Factory Boy](https://factoryboy.readthedocs.io/en/stable/index.html "Documentacion Factory Boy")

```shell
pip install factory_boy
```

factories.py
```python
import factory
from faker import Faker

from tests.providers.general_providers import EmailProvider
from apps.usuario.models import Usuario, Rol

fake = Faker()
fake.add_provider(EmailProvider)


class RolFactory(factory.Factory):
    class Meta:
        model = Rol

    rol = 'admin'
	
class UsuarioComunFactory(factory.Factory):
    class Meta:
        model = Usuario
    
    nombres = "Oliver"
    username = "oliver"
    email = fake.email()
    is_staff = False
	

class UsuarioAdminFactory(factory.Factory):
    class Meta:
        model = Usuario
    
    nombres = "Oliver"
    username = "oliver"
    is_staff = True
    is_superuser = True
    rol = factory.SubFactory(RolFactory)
```

# TestCase

```python
from django.test import TestCase
from tests.factories import UsuarioAdminFactory, UsuarioComunFactory


class UsuarioTestCase(TestCase):
    def setUp(self):
        self.common_user = UsuarioComunFactory.create()
        self.superuser = UsuarioAdminFactory.create()
    
    def test_common_user_creation(self):
        self.assertEqual(self.common_user.is_active, True)
        self.assertEqual(self.common_user.is_staff, False)
        self.assertEqual(self.common_user.is_superuser, False)
    
    def test_superuser_creation(self):
        self.assertEqual(self.superuser.is_staff, True)
        self.assertEqual(self.superuser.is_superuser, True)
```

# Client


```python
from django.test import TestCase, Client

class UsuarioTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.common_user = UsuarioComunFactory.create()
        self.superuser = UsuarioAdminFactory.create()
		
	def test_superuser_creation(self):
        self.assertEqual(self.superuser.is_staff, True)
        self.assertEqual(self.superuser.is_superuser, True)

    def test_login(self):
        self.common_user.set_password('oliver')
        self.common_user.save()
        response = self.client.login(username='oliver', password='oliver')
        self.assertEquals(response, True)

    def test_login_fail(self):
        self.common_user.set_password('oliver')
        self.common_user.save()
        response = self.client.login(username='oliver', password='oliver1')
        self.assertEquals(response, False)

    def test_users_list(self):
        self.superuser.set_password('oliver')
        self.superuser.save()
        self.client.login(username='oliver', password='oliver')
        response = self.client.get('/usuarios/listado_usuarios/', 
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()), 1)
```

[Documentacion Testing Django](https://docs.djangoproject.com/en/4.0/topics/testing/tools/ "Documentacion Testing Django")
