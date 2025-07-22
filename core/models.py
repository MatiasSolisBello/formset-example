from django.db import models

# Create your models here.
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100, verbose_name="Autor")
    
    def __str__(self):
        return self.name
    
    
class Book(models.Model):
    author = models.ForeignKey(Author, 
                               on_delete=models.CASCADE, 
                               related_name='books')
    title = models.CharField(max_length=200, verbose_name="Titulo")
    published_year = models.IntegerField(verbose_name="Año de Publicación")
    
    def __str__(self):
        return f'{self.title} by {self.author.name}'
    
    
    