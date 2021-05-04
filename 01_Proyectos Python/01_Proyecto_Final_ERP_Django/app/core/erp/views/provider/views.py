from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from core.erp.forms import ProviderForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Provider



class ProviderListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Provider
    template_name = 'provider/list.html'
    permission_required = 'erp.view_provider'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Provider.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Proveedores'
        context['create_url'] = reverse_lazy('erp:provider_create')
        context['list_url'] = reverse_lazy('erp:provider_list')
        context['entity'] = 'Proveedores'
        return context


class ProviderCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Provider
    form_class = ProviderForm
    template_name = 'provider/create.html'
    success_url = reverse_lazy('erp:provider_list')
    permission_required = 'erp.add_provider'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha introducido ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación un Proveedor'
        context['entity'] = 'Proveedores'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context


class ProviderUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Provider
    form_class = ProviderForm
    template_name = 'provider/create.html'
    success_url = reverse_lazy('erp:provider_list')
    permission_required = 'erp.change_provider'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha introducido ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición un Proveedor'
        context['entity'] = 'Proveedores'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class ProviderDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Provider
    template_name = 'provider/delete.html'
    success_url = reverse_lazy('erp:provider_list')
    permission_required = 'erp.delete_provider'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de un Proveedor'
        context['entity'] = 'Proveedores'
        context['list_url'] = self.success_url
        return context