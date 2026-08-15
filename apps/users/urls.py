# """
# File: core/urls.py
# Description: The master routing file for the entire backend. Directs traffic to the specific apps.
# """

# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # Authentication
#     path('api/auth/login/', TokenObtainPairView.as_view(), name='api-token-obtain'),
#     path('api/auth/refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

#     # Our E-Commerce APIs
#     path('api/users/', include('apps.users.urls')),
#     path('api/products/', include('apps.products.urls')),
#     path('api/orders/', include('apps.orders.urls')),
# ]

# # CRUCIAL FOR LOCAL WINDOWS DEVELOPMENT:
# # This tells Django how to serve uploaded media files (like product images) on your local machine.
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path

urlpatterns = [
    # We will add user-specific routes (like registering) here later
]