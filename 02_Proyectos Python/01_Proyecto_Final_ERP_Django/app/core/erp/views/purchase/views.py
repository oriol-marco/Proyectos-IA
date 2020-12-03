import json
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from xhtml2pdf import pisa

from config import settings
from core.erp.forms import PurchaseForm, ProviderForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Inventory, Purchase, Provider, Product


class PurchaseListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchase/list.html'
    permission_required = 'erp.view_purchase'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for c in Purchase.objects.all():
                    data.append(c.toJSON())
            elif action == 'search_details_prod':
                data = []
                for c in Inventory.objects.filter(purch_id=request.POST['id']):
                    data.append(c.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = reverse_lazy('erp:purchase_create')
        context['title'] = 'Listado de Compras'
        context['list_url'] = reverse_lazy('erp:purchase_list')
        context['entity'] = 'Compras'
        return context


class PurchaseCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Purchase
    template_name = 'purchase/create.html'
    form_class = PurchaseForm
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'erp.add_purchase'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validate_prov(self):
        data = {'valid': True}
        try:
            type = self.request.POST['type']
            obj = self.request.POST['obj'].strip()
            if type == 'name':
                if Provider.objects.filter(name__iexact=obj):
                    data['valid'] = False
            elif type == 'CIF':
                if Provider.objects.filter(CIF__iexact=obj):
                    data['valid'] = False
        except:
            pass
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                with transaction.atomic():
                    compras = json.loads(request.POST['compras'])
                    comp = Purchase()
                    comp.prov_id = compras['prov']
                    comp.date_joined = compras['date_joined']
                    comp.subtotal = float(compras['subtotal'])
                    comp.iva = float(compras['iva'])
                    comp.total = float(compras['total'])
                    comp.save()

                    for p in compras['products']:
                        prod = Product.objects.get(pk=p['id'])
                        inv = Inventory()
                        inv.purch_id = comp.id
                        inv.prod_id = prod.id
                        inv.cant = int(p['cant'])
                        inv.saldo = inv.cant
                        inv.price = float(p['cost'])
                        inv.total = inv.cant * float(inv.price)
                        inv.save()
                    data = {'id': comp.id}
                    #comp.calculate_invoice()

            elif action == 'search_products':
                data = []
                term = request.POST['term']
                search = Product.objects.filter().order_by('name')
                if len(term):
                    search = search.filter(name__icontains=term)
                    search = search[0:10]
                for p in search:
                    item = p.toJSON()
                    stock = p.get_stock()
                    item['stock'] = stock
                    item['text'] = '{} / {}'.format(p.name, stock)
                    data.append(item)
            elif action == 'search_prov':
                data = []
                for p in Provider.objects.filter(name__icontains=request.POST['term']).order_by('name')[0:10]:
                    item = p.toJSON()
                    item['value'] = p.name
                    data.append(item)
            elif action == 'validate_prov':
                return self.validate_prov()
            elif action == 'create_prov':
                c = Provider()
                c.name = request.POST['name']
                c.mobile = request.POST['mobile']
                c.address = request.POST['address']
                c.email = request.POST['email']
                c.CIF = request.POST['CIF']
                c.save()
            else:
                data['error'] = 'No ha introducido una opción válida'
        except Exception as e:
            data['error'] = str(e)
        finally:
            print(data)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['formProv'] = ProviderForm()
        context['list_url'] = self.success_url
        context['title'] = 'Nuevo registro de una Compra'
        context['action'] = 'add'
        return context


class PurchaseUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase/create.html'
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'erp.change_purchase'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                prods = Product.objects.filter(name__icontains=request.POST['term'])[0:10]
                for i in prods:
                    item = i.toJSON()
                    item['value'] = i.name
                    data.append(item)
            elif action == 'edit':
                with transaction.atomic():
                    compras = json.loads(request.POST['compras'])
                    #purchase = Purchase.objects.get(pk=self.get_object().id)
                    purchase = self.get_object()
                    purchase.date_joined = compras['date_joined']
                    purchase.prov_id = compras['prov']
                    purchase.subtotal = float(compras['subtotal'])
                    purchase.iva = float(compras['iva'])
                    purchase.total = float(compras['total'])
                    purchase.save()
                    purchase.inventory_set.all().delete()
                    for i in compras['products']:
                        inv = Inventory()
                        inv.purchase_id = purchase.id
                        inv.prod_id = i['id']
                        inv.cant = int(i['cant'])
                        inv.price = float(i['price'])
                        inv.subtotal = float(i['subtotal'])
                        inv.save()
                    data = {'id': purchase.id}
            else:
                data['error'] = 'No ha introducido ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_details_product(self):
        data = []
        try:
            for i in Inventory.objects.filter(sale_id=self.get_object().id):
                item = i.prod.toJSON()
                item['cant'] = i.cant
                data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de una Compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.get_details_product())
        return context


class PurchaseDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'purchase/delete.html'
    success_url = reverse_lazy('erp:purchase_list')
    permission_required = 'delete_purchase'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.get_object().delete()
        except Exception as e:
            data['error'] = str(e)
        return HttpResponse(json.dumps(data), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una compra'
        context['entity'] = 'Compras'
        context['list_url'] = self.success_url
        return context


class PurchaseInvoicePdfView(View):

    def link_callback(self, uri, rel):
        """
        Convert HTML URIs to absolute system paths so xhtml2pdf can access those
        resources
        """
        # use short variable names
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /static/media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        # convert URIs to absolute system paths
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri  # handle absolute uri (ie: http://some.tld/foo.png)

        # make sure that file exists
        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('purchase/invoice.html')
            context = {
                'purchase': Purchase.objects.get(pk=self.kwargs['pk']),
                'comp': {'name': 'TECLA2 S.A.', 'CIF': '9999999999999', 'address': 'Barcelona, España'},
                'icon': '{}{}'.format(settings.MEDIA_URL, 'logo1.png')
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
            pisaStatus = pisa.CreatePDF(
                html, dest=response,
                link_callback=self.link_callback
            )
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('erp:purchase_list'))
