from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator

from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView


from core.forms import AuthorForm, ConfirmDeleteForm
from .models import Author
from django_tables2 import SingleTableView
from .tables import AuthorTable

# Create your views here.
class AuthorView(SingleTableView):
    model = Author
    template_name = "core/index.html"
    
class AuthorList(SingleTableView):
    model = Author
    table_class = AuthorTable
    template_name = "core/list_authors.html"
    
class AuthorCreate(SuccessMessageMixin, FormView):
    model = Author
    form_class = AuthorForm
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    success_message = "Author created successfully"
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response
    
class AuthorEdit(SuccessMessageMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('list_authors')
    template_name = 'core/confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in kwargs:
            context['form'] = ConfirmDeleteForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ConfirmDeleteForm(request.POST, instance=self.object)
        if form.is_valid():
            return self.delete(request, *args, **kwargs)
        else:
            return self.render_to_response(
                self.get_context_data(form=form),
            )