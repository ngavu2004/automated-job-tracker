from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import routers
from django.views.static import serve
from .service_provider import views

router = routers.DefaultRouter()
# router.register(r'emails', views.EmailViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'jobs', views.JobAppliedViewSet)
router.register(r'fetch_logs', views.FetchLogViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path("auth/google/login/", views.GoogleOAuthLoginRedirect.as_view()),
    path("auth/google/callback/", views.GoogleOAuthCallback.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('task_status/<str:task_id>/', views.TaskStatusView.as_view()),
]


# Serve static and media files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # For production, you can use re_path to serve static and media files
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]