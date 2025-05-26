from django.urls import include, path
from rest_framework import routers

from .service_provider import views

router = routers.DefaultRouter()
# router.register(r'emails', views.EmailViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'jobs', views.JobAppliedViewSet)
# router.register(r'fetch_logs', views.FetchLogViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path("auth/google/login/", views.GoogleOAuthLoginRedirect.as_view()),
    path("auth/google/callback/", views.GoogleOAuthCallback.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]