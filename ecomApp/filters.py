import django_filters
from .models import Product

# This class defines custom filtering options for the Product model
class ProductFilter(django_filters.FilterSet):
    # Filter for products with price greater than or equal to the given value
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')

    # Filter for products with price less than or equal to the given value
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')

    # Custom boolean filter to check if the product is in stock or not
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product  # The model on which filtering will be applied
        # These are the fields that will be available for filtering
        fields = ['category', 'min_price', 'max_price', 'in_stock']

    # Custom method for filtering based on stock availability
    def filter_in_stock(self, queryset, name, value):
        if value:
            # If in_stock is True, return products with stock greater than 0
            return queryset.filter(stock__gt=0)
        else:
            # If in_stock is False, return products with stock less than or equal to 0
            return queryset.filter(stock__lte=0)
