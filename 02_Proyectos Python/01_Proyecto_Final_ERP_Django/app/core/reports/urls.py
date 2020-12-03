from django.urls import path

from core.reports.views import ReportSaleView
from core.reports.views import ReportPurchaseView

urlpatterns = [
    # reports
    path('sale/', ReportSaleView.as_view(), name='sale_report'),
    path('purchase/', ReportPurchaseView.as_view(), name='purchase_report'),
]