from django.utils import timezone
from django.db.models import Sum, F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsAdminOrSales
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer
from .services import cancel_order


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        from django.db.models import Q
        queryset = Order.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', None)
        status_filter = self.request.query_params.get('status', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        customer = self.request.query_params.get('customer', None)

        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) | Q(customer__name__icontains=search)
            )
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
        if customer:
            queryset = queryset.filter(customer_id=customer)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.IsAuthenticated()]
        return [IsAdminOrSales()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def set_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status == Order.Status.DIBATALKAN:
            order = cancel_order(order)
        elif new_status in (Order.Status.DIPROSES, Order.Status.SELESAI):
            order.status = new_status
            order.save(update_fields=['status'])
        else:
            return Response({'error': 'Status tidak valid'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data)


class OrderStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        orders_qs = Order.objects.all()

        # Extract filters
        customer_id = request.query_params.get('customer')
        order_status = request.query_params.get('status')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        search = request.query_params.get('search')

        # Apply filters
        if customer_id:
            orders_qs = orders_qs.filter(customer_id=customer_id)
        if order_status:
            orders_qs = orders_qs.filter(status=order_status)
        if start_date:
            orders_qs = orders_qs.filter(created_at__date__gte=start_date)
        if end_date:
            orders_qs = orders_qs.filter(created_at__date__lte=end_date)
        if search:
            from django.db.models import Q
            orders_qs = orders_qs.filter(
                Q(order_number__icontains=search) | Q(customer__name__icontains=search)
            )

        # Filters this month stats
        orders_this_month = orders_qs.filter(
            created_at__year=now.year, created_at__month=now.month
        )
        orders_this_month_active = orders_this_month.exclude(status=Order.Status.DIBATALKAN)

        revenue = OrderItem.objects.filter(
            order__in=orders_this_month_active
        ).aggregate(total=Sum(F('quantity') * F('price_at_order')))['total'] or 0

        pending_orders_count = orders_qs.filter(status=Order.Status.PENDING).count()
        low_stock_products_count = Product.objects.filter(
            stock__lte=F('low_stock_threshold')
        ).count()

        return Response({
            'orders_this_month': orders_this_month.count(),
            'pending_orders': pending_orders_count,
            'low_stock_products': low_stock_products_count,
            'revenue_this_month': str(revenue),
        })
