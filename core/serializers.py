from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers

from .models import CalendarEvent, Habit, Task


def get_week_start(target_date):
    return target_date - timedelta(days=target_date.weekday())


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    firstName = serializers.CharField(source='first_name', read_only=True)
    lastName = serializers.CharField(source='last_name', read_only=True)
    displayName = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    isStaff = serializers.BooleanField(source='is_staff', read_only=True)
    isSuperuser = serializers.BooleanField(source='is_superuser', read_only=True)

    def get_displayName(self, user):
        full_name = user.get_full_name().strip()
        return full_name or user.username

    def get_initials(self, user):
        parts = [part[:1].upper() for part in user.get_full_name().split() if part]
        if parts:
            return ''.join(parts[:2])
        return user.username[:2].upper()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs.get('username'),
            password=attrs.get('password'),
        )
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        if not user.is_active:
            raise serializers.ValidationError('This user is inactive.')
        attrs['user'] = user
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    date = serializers.DateField(source='due_date')
    estimatedMinutes = serializers.IntegerField(source='estimated_minutes', allow_null=True, required=False)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'priority', 'status', 'date', 'tags', 'estimatedMinutes']


class HabitSerializer(serializers.ModelSerializer):
    completedDays = serializers.SerializerMethodField()
    totalDays = serializers.IntegerField(source='total_days', read_only=True)

    class Meta:
        model = Habit
        fields = ['id', 'name', 'icon', 'color', 'streak', 'completedDays', 'totalDays', 'category']

    def get_completedDays(self, habit):
        request = self.context.get('request')
        week_start_raw = request.query_params.get('week_start') if request else None
        today = timezone.localdate()
        if week_start_raw:
            try:
                week_start = datetime.strptime(week_start_raw, '%Y-%m-%d').date()
            except ValueError:
                week_start = get_week_start(today)
        else:
            week_start = get_week_start(today)

        week_dates = [week_start + timedelta(days=index) for index in range(7)]
        completed_dates = set(
            habit.completions.filter(
                date__gte=week_start,
                date__lte=week_start + timedelta(days=6),
                completed=True,
            ).values_list('date', flat=True)
        )
        return [day in completed_dates for day in week_dates]


class HabitToggleSerializer(serializers.Serializer):
    date = serializers.DateField()


class CalendarEventSerializer(serializers.ModelSerializer):
    time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])
    taskId = serializers.IntegerField(source='task_id', allow_null=True, required=False)

    class Meta:
        model = CalendarEvent
        fields = ['id', 'title', 'date', 'time', 'duration', 'color', 'taskId']
