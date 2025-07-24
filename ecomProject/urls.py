from django.contrib import admin
from django.urls import path, include
from ecomApp.views import EmailTokenObtainPairView

from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecomApp.urls')),
    path('api/token/', EmailTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

