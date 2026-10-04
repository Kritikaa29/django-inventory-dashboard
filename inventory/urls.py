from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('staff/', views.staff_list, name='staff_list'),
    path('edit/<int:pk>/', views.edit_product, name='edit_product'), # <--- YE LINE ADD KAREIN
    path('delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('delete-staff/<int:pk>/', views.delete_staff, name='delete_staff'),
    # Add this line inside your urlpatterns list:
path('orders/', views.order_list, name='order_list'),
path('export/', views.export_products_csv, name='export_products_csv'),
]