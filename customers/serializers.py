from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'type', 'phone', 'address', 'pic_name',
            'city', 'province', 'notes', 'created_at', 'updated_at',
        ]
