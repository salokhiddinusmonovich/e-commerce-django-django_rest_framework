from django.urls import path

from . import views


urlpatterns = [
    path('cart/', views.CartByOwnerListAPIView.as_view(), name='cart'),
    path('add/<int:pk>/', views.add_order, name='add_order'),
    path('put/<int:pk>/', views.put_order, name='put_order'),
]