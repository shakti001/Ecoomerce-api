from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions,status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache

from .models import User ,Category, Product,Cart,Order,OrderItem
from .serializers import RegisterSerializer, UserProfileSerializer ,CategorySerializer, ProductSerializer, CartSerializer, OrderItemSerializer,OrderSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .token_serializers import EmailTokenObtainPairSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication

from.pagination import TenPerPagePagination
from .filters import ProductFilter
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Custom token obtain view using the EmailTokenObtainPairSerializer
class EmailTokenObtainPairView(TokenObtainPairView):
    # Replaces the default serializer with custom one that uses email for authentication
    serializer_class = EmailTokenObtainPairSerializer


# ViewSet to handle user registration and profile operations
class UserViewSet(viewsets.GenericViewSet):
    """
    Handles user registration and profile actions
    """
    queryset = User.objects.all()  # Base queryset for reference (can be filtered in methods)

    # Custom action to register a new user
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        # Use the RegisterSerializer to validate and save user data
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # Save the new user
        return Response(serializer.data)  # Return the created user's data

    # Custom action to retrieve or update the logged-in user's profile
    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        if request.method == 'GET':
            # If GET request, return the current user's profile data
            serializer = UserProfileSerializer(request.user)
        else:
            # If PUT request, update the user's profile with provided data
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Save updated profile
        return Response(serializer.data)  # Return profile data (either fetched or updated)
    
# Product and category api'scode below 
# Cache timeout duration set to 1 hour (in seconds)
CACHE_TIMEOUT = 60 * 60  # 1 hour

# ViewSet for managing Category objects
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]  # Allow only admin to modify, others can read
    pagination_class = TenPerPagePagination  # Custom pagination - 10 items per page

    def get_queryset(self):
        # Try to fetch categories from cache
        cached_categories = cache.get("categories")
        if cached_categories is None:
            # If not in cache, fetch from DB and cache the result
            categories = Category.objects.all()
            cache.set("categories", categories, CACHE_TIMEOUT)
            return categories
        return cached_categories  # Return cached data if available

# ViewSet for managing Product objects
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = TenPerPagePagination
    filterset_class = ProductFilter  # Enables filtering like price range, stock, etc.

    def get_queryset(self):
        # Try to fetch products from cache
        cached_products = cache.get("products")
        if cached_products is None:
            # If not in cache, fetch from DB with category prefetching and cache it
            products = Product.objects.select_related('category').all()
            print(products)  # Debug print, can be removed in production
            cache.set("products", products, CACHE_TIMEOUT)
            return products
        return cached_products  # Return cached data if available

    def perform_update(self, serializer):
        # On product update, clear the cache so updated data can be fetched next time
        instance = serializer.save()
        cache.delete("products")
        return instance

    def perform_create(self, serializer):
        # On product creation, clear the cache so new data can be fetched
        instance = serializer.save()
        cache.delete("products")
        return instance

    def perform_destroy(self, instance):
        # On product deletion, clear the cache so next fetch reflects changes
        instance.delete()
        cache.delete("products")

# Custom JWT authentication that allows unauthenticated access (optional auth)
class OptionalJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception:
            return None  # If JWT fails, return None instead of throwing error


# ViewSet for managing Cart functionality
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    authentication_classes = [OptionalJWTAuthentication]  # Auth optional for cart operations

    def get_queryset(self):
        # Return only carts belonging to the authenticated user
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        # Handle adding a product to the cart
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)

        # Use authenticated user or None
        user = request.user if request.user.is_authenticated else None
        print(user)  # Debug print

        # Get or create the cart item
        cart, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )

        # If already exists, update the quantity
        if not created:
            cart.quantity = quantity
            cart.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Custom route to get cart by user ID: /cart/user/{user_id}/
    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_cart(self, request, user_id=None):
        # Fetch all cart items for a given user
        carts = Cart.objects.filter(user_id=user_id)
        serializer = self.get_serializer(carts, many=True)
        return Response(serializer.data)

    # Import necessary modules and classes
class OrderViewSet(viewsets.ViewSet):
    # All order objects
    queryset = Order.objects.all()
    # Serializer to be used
    serializer_class = OrderSerializer
    # JWT-based authentication
    authentication_classes = [JWTAuthentication]

    # Custom action for placing an order
    @action(detail=False, methods=['post'])
    def place_order(self, request):
        # Get authenticated user, or None if anonymous
        user = request.user if request.user.is_authenticated else None

        # Ensure session exists and get session key
        session_key = request.session.session_key or request.session.save()

        # Fetch cart items based on user or session
        if user:
            cart_items = Cart.objects.filter(user=user)
        else:
            cart_items = Cart.objects.filter(session_key=request.session.session_key)

        # If cart is empty, return error
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new order associated with the user (or anonymous)
        order = Order.objects.create(user=user)

        # Loop through all cart items to create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Deduct ordered quantity from product stock
            item.product.stock -= item.quantity
            item.product.save()

        # Clear the cart after placing the order
        cart_items.delete()

        # 🔔 Send WebSocket notification to user via Django Channels
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{request.user.id}",  # Group name
                {
                    'type': 'send_notification',  # Consumer handler method
                    'message': f"Order #{order.id} placed successfully!"
                }
            )
            print("Notification sent successfully!")
        except Exception as e:
            print("Failed to send notification:", str(e))

        # Return success response
        return Response({'status': 'Order placed'}, status=status.HTTP_201_CREATED)

    # Admin-only action to update the order status
    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReadOnly])
    def update_status(self, request, pk=None):
        try:
            # Fetch the order by primary key
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the new status from request
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        # Update and save the new status
        order.status = new_status
        order.save()

        # 🔔 Send status update notification
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f"user_{order.user.id}",
                {
                    'type': 'send_notification',
                    'message': f"Order #{order.id} status updated to {new_status.title()}!"
                }
            )
            print("Status update notification sent successfully!")
        except Exception as e:
            print("Failed to send notification:", str(e))

        return Response({'status': f'Order status updated to {new_status}'})
