from rest_framework import viewsets, permissions
from accounts.permissions import IsAdminOrSales
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        queryset = Customer.objects.all().order_by('name')
        search = self.request.query_params.get('search', None)
        customer_type = self.request.query_params.get('type', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        if customer_type:
            queryset = queryset.filter(type=customer_type)
        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [IsAdminOrSales()]
