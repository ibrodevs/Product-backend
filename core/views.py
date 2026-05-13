from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CalendarEvent, Habit, HabitCompletion, Task
from .serializers import (
    CalendarEventSerializer,
    HabitSerializer,
    HabitToggleSerializer,
    LoginSerializer,
    TaskSerializer,
    UserSerializer,
)
from .services import build_analytics_payload, build_dashboard_payload


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class LogoutView(APIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-due_date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).prefetch_related('completions')

    def perform_create(self, serializer):
        habit = serializer.save(user=self.request.user)
        habit.recalculate_metrics()
        habit.save(update_fields=['streak', 'total_days'])

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        habit = self.get_object()
        serializer = HabitToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_date = serializer.validated_data['date']

        completion, created = HabitCompletion.objects.get_or_create(
            habit=habit,
            date=target_date,
            defaults={'completed': True},
        )
        if not created:
            completion.completed = not completion.completed
            completion.save(update_fields=['completed'])

        habit.recalculate_metrics(today=timezone.localdate())
        habit.save(update_fields=['streak', 'total_days'])
        return Response(HabitSerializer(habit, context={'request': request}).data)


class CalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarEventSerializer

    def get_queryset(self):
        queryset = CalendarEvent.objects.filter(user=self.request.user).select_related('task')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset.order_by('date', 'time')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
def dashboard_view(request):
    return Response(build_dashboard_payload(request.user, request))


@api_view(['GET'])
def analytics_view(request):
    return Response(build_analytics_payload(request.user))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_view(request):
    return Response({'ok': True})
