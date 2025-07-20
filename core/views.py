from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView, UpdateView


from core.forms import AuthorForm, BookFormSet, ConfirmDeleteForm
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
    
    
class AuthorCreate(SuccessMessageMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    success_message = "Author and books created successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = BookFormSet(self.request.POST, 
                                             prefix='authorbook_set')
        else:
            context['formset'] = BookFormSet(prefix='authorbook_set')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
    
class AuthorEdit(SuccessMessageMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    success_message = "Author and books updated successfully"

    def get_object(self, queryset=None):
        try:
            return Author.objects.get(pk=self.kwargs['pk'])
        except Author.DoesNotExist as exc:
            raise Http404("Author not found") from exc

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = BookFormSet(
                self.request.POST,
                instance=self.object,
                prefix='authorbook_set'
            )
        else:
            context['formset'] = BookFormSet(
                instance=self.object,
                prefix='authorbook_set'
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, self.success_message)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        return render(self.request, self.template_name, context)
    

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('list_authors')
    template_name = 'core/confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            return Author.objects.get(id=pk)
        except Author.DoesNotExist as e:
            raise Http404(e)

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