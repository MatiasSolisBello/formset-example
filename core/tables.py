import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2 import A, LinkColumn
from core.models import Author

class AuthorTable(tables.Table):
    class Meta:
        model = Author
        fields = [
            'name'
        ]