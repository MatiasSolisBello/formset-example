from django.urls import include, path
from core.views import ListAuthors

urlpatterns = [
    # url / vista /alias
    path('', ListAuthors.as_view(), name="list_authors"),
    
]