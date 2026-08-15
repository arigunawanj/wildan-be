from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'unit', 'stock', 'price',
            'low_stock_threshold', 'created_at', 'updated_at',
        ]

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Harga satuan tidak boleh bernilai negatif.")
        return value
