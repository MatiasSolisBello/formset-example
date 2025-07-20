import django_tables2 as tables
from django.utils.translation import gettext_lazy as _
from django_tables2 import A, LinkColumn
from core.models import Author

class AuthorTable(tables.Table):
    edit = LinkColumn(
        'edit_authors',
        args=[A('pk')],
        verbose_name=_("Editar"),
        text=_("Editar"),
        orderable=False,
        attrs={
            'a': {
                'class': 'btn btn-warning'
            }
        }
    )

    delete = LinkColumn(
        'delete_authors',
        args=[A('pk')],
        verbose_name=_("Eliminar"),
        text=_("Eliminar"),
        orderable=False,
        attrs={
            'a': {
                'class': 'btn btn-danger'
            }
        }
    )
    
    class Meta:
        model = Author
        fields = ['name', 'edit', 'delete']
        empty_text = "Sin registros"