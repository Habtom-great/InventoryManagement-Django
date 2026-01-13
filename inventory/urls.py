from django.urls import path 

from django.urls import path, re_path

from . import views 

urlpatterns = [
    path('', views.StockListView.as_view(), name='inventory'), 
    path('new', views.StockCreateView.as_view(), name='new-stock'), 
    path('stock/<pk>/edit', views.StockUpdateView.as_view(), name='edit-stock'), 
    path('stock/<pk>/delete', views.StockDeleteView.as_view(), name='delete-stock'), 
    
    ]
