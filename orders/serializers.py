from rest_framework import serializers
from .models import Order, OrderItem
from .services import create_order, InsufficientStockError


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_order']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'status',
            'created_by', 'created_by_username', 'items', 'total',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['order_number', 'status', 'created_by']

    def get_total(self, obj):
        return sum(item.quantity * item.price_at_order for item in obj.items.all())


class OrderCreateSerializer(serializers.Serializer):
    customer = serializers.IntegerField()
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Pesanan harus punya minimal 1 item.')
        return value

    def create(self, validated_data):
        request = self.context['request']
        try:
            return create_order(
                customer_id=validated_data['customer'],
                items=[
                    {'product_id': i['product_id'], 'quantity': i['quantity']}
                    for i in validated_data['items']
                ],
                created_by=request.user,
            )
        except InsufficientStockError as exc:
            raise serializers.ValidationError(str(exc))
