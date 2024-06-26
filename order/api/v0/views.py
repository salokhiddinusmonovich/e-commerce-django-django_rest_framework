from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache



from products.models import Product
from .permissions import IsOrderOwner
from .serializers import OrderSerializer
from order.models import Order, OrderItem


class CartByOwnerListAPIView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.request.user.pk
        cardorederby = cache.get(f'cardorederby_{pk}')
        if cardorederby is None:
            cardorederby =  Order.objects.all()
            cache.set('cardorederby_{pk}', cardorederby)
        return cardorederby

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.filter(customer=self.request.user, ordered=False)
    #     return qs



@api_view(['POST'])
@permission_classes([IsOrderOwner])
def add_order(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, order_created = Order.objects.get_or_create(
        customer=request.user,
        ordered=False
    )


    try:
        order_item, order_item_created = OrderItem.objects.get_or_create(
            product=product,
            customer=request.user,
            ordered=False,
            order=order

        )
    except IntegrityError:
        order_item, order_item_created = OrderItem.objects.get_or_create(
            product=product,
            customer=request.user,
            quantity=1,
            ordered=False,
            order=order

        )
    order_item.set_total_price()
    if not order_item_created:
        order_item.quantity += 1
        order_item.save()
        order_item.set_total_price()
        return Response({'message': "1 ga oshirildi"}, status=status.HTTP_201_CREATED)
    return Response({'message': "order yaratildi"}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsOrderOwner])
def put_order(request, pk):
    product = get_object_or_404(Product, pk=pk)
    order, order_created = Order.objects.get_or_create(
        customer=request.user,
        ordered=False
    )

    try:
        order_item, order_item_created = OrderItem.objects.get_or_create(
            product=product,
            customer=request.user,
            ordered=False,
            order=order

        )
    except IntegrityError:
        order_item, order_item_created = OrderItem.objects.get_or_create(
            product=product,
            customer=request.user,
            quantity=1,
            ordered=False,
            order=order

        )
    order_item.set_total_price()
    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
        order_item.set_total_price()
        return Response({'message': "1 ga kamaydi"}, status=status.HTTP_201_CREATED)
    else:
        order_item.delete()
        return Response({'message': "order uchirildi"}, status=status.HTTP_201_CREATED)


