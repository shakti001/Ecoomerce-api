from rest_framework import serializers
from .models import User, Category, Product, Cart, Order,OrderItem
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'