from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CategoryViewSet, ProductViewSet, CartViewSet,OrderViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet,basename='category')
router.register(r'products', ProductViewSet ,basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'order', OrderViewSet, basename='orders')
urlpatterns = [
    path('', include(router.urls)),
]
