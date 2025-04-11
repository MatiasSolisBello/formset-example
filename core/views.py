from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Author
from django_tables2 import SingleTableView
from .tables import AuthorTable

# Create your views here.
class ListAuthors(SingleTableView):
    model = Author
    table_class = AuthorTable
    template_name = "core/list_authors.html"