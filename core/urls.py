from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    CalendarEventViewSet,
    HabitViewSet,
    LoginView,
    LogoutView,
    MeView,
    TaskViewSet,
    analytics_view,
    dashboard_view,
    health_view,
)

router = DefaultRouter()
router.trailing_slash = '/?'
router.register('tasks', TaskViewSet, basename='task')
router.register('habits', HabitViewSet, basename='habit')
router.register('events', CalendarEventViewSet, basename='event')

urlpatterns = [
    re_path(r'^auth/login/?$', LoginView.as_view(), name='login'),
    re_path(r'^auth/logout/?$', LogoutView.as_view(), name='logout'),
    re_path(r'^auth/me/?$', MeView.as_view(), name='me'),
    re_path(r'^dashboard/?$', dashboard_view, name='dashboard'),
    re_path(r'^analytics/?$', analytics_view, name='analytics'),
    re_path(r'^health/?$', health_view, name='health'),
    re_path(r'^', include(router.urls)),
]
