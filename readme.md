# Ejecución de proyecto

Crear entorno virtual.
```bash
sudo apt-get update
virtualenv venv
source venv/bin/activate
```

Instalar paquetes necesarios
```bash
pip install -r requirements.txt
```

Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

Crear superusuario
```bash
python manage.py createsuperuser
```


Ejecutar servidor
```bash
python manage.py runserver
```

## Otros comandos
Verificar version de Python y Django respectivamente
```bash
python --version
python -m django --version
```