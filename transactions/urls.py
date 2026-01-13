from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [

    path('suppliers/', views.SupplierListView.as_view(), name='suppliers-list'),
    path('suppliers/new/', views.SupplierCreateView.as_view(), name='new-supplier'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='edit-supplier'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='delete-supplier'),


    # ---------------- PURCHASES ----------------
    path('purchases/', views.PurchaseView.as_view(), name='purchases-list'),
    path('purchases/select-supplier/', views.SelectSupplierView.as_view(), name='select-supplier'),
    path('purchases/new/<int:pk>/', views.PurchaseCreateView.as_view(), name='new-purchase'),
    path('purchases/delete/<int:pk>/', views.PurchaseDeleteView.as_view(), name='delete-purchase'),
    path('purchases/bill/<int:billno>/', views.PurchaseBillView.as_view(), name='purchase-bill'),

    # ---------------- SALES ----------------
    path('sales/', views.SaleView.as_view(), name='sales-list'),
    path('sales/new/', views.SaleCreateView.as_view(), name='new-sale'),
    path('sales/edit/<int:pk>/', views.SaleUpdateView.as_view(), name='edit-sale'),
    path('sales/<int:pk>/delete/', views.SaleDeleteView.as_view(), name='delete-sale'),
    path('sales/<int:billno>/', views.SaleBillView.as_view(), name='sale-bill'),

    # ---------------- SALES EXPORTS ----------------
    path('sales/<int:billno>/export-excel/', views.export_sale_excel, name='export-sale-excel'),
    path('sales/<int:billno>/export-pdf/', views.export_sale_pdf, name='export-sale-pdf'),
    path('sales/<int:billno>/export-word/', views.export_sale_word, name='export-sale-word'),
]
