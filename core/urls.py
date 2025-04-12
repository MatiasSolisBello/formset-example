from django.urls import path
from core.views import AuthorCreate, AuthorList, AuthorView, AuthorEdit, AuthorDelete

urlpatterns = [
    # url / vista /alias
    path('', AuthorView.as_view(), name="index"),
    path('authors', AuthorList.as_view(), name="list_authors"),
    path('create', AuthorCreate.as_view(), name="create_authors"),
    path('edit/<int:pk>/', AuthorEdit.as_view(), name="edit_authors"),
    path('delete/<int:pk>/', AuthorDelete.as_view(), name="delete_authors"),
    
]