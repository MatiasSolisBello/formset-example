from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, UpdateView


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
    
class AuthorCreate(SuccessMessageMixin, View):
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    success_message = "Author and books created successfully"

    def get(self, request, *args, **kwargs):
        form = AuthorForm()
        formset = BookFormSet()
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
        })

    def post(self, request, *args, **kwargs):
        form = AuthorForm(request.POST)
        formset = BookFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            author = form.save()
            formset.instance = author
            formset.save()
            messages.success(request, self.success_message)
            return redirect(self.success_url)
        return render(request, self.template_name, {
            'form': form,
            'formset': formset,
        })

    
class AuthorEdit(SuccessMessageMixin, UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'core/edit_author.html'
    success_url = reverse_lazy('list_authors')
    
    def get_object(self):
        try:
            obj = Author.objects.get(id=self.kwargs['pk'])
        except Author.DoesNotExist as exc:
            raise Http404(exc) from exc
        print(obj)
        return obj
    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        form = AuthorForm(instance=obj)
        formset = BookFormSet(instance=obj, prefix='authorbook_set')
        return render(request, self.template_name, {
            'instance': obj,
            'form': form,
            'formset': formset,
        })
        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        formset = BookFormSet(
            self.request.POST, instance=self.object,
            prefix='authorbook_set'
        )
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Author and books updated successfully")
            return self.form_valid(form)
        else:
            print('1.-', form.errors)
            print('2.- ', formset.errors)
            return self.form_invalid(form)
    

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('list_authors')
    template_name = 'core/confirm_delete.html'
    
    def get(self, request, *args, **kwargs):
        print(request.GET)
        return super().get(request, *args, **kwargs)
    
    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            return Author.objects.get(id=pk)
        except Author.DoesNotExist as e:
            raise Http404(e)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('get_context_data: ', context)
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