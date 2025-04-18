from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Импорт настроек
from django.conf.urls.static import static # Импорт для статики/медиа
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/v1/contacts/', include('contacts.urls')),
    path('api/v1/news/', include('news.urls')),
    path('api/v1/catalog/', include('catalog.urls')),
    path('api/v1/', include('quizzes.urls')),
    path('api/v1/', include('requests_app.urls')),
    path('api/v1/analytics/', include('analytics_app.urls')),
    path('api/auth/', include('authentication.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
