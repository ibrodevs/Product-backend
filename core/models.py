from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    class Status(models.TextChoices):
        TODO = 'todo', 'To Do'
        IN_PROGRESS = 'in-progress', 'In Progress'
        DONE = 'done', 'Done'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    due_date = models.DateField()
    tags = models.JSONField(default=list, blank=True)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self) -> str:
        return self.title


class Habit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, default='Target')
    color = models.CharField(max_length=20, default='#403580')
    streak = models.PositiveIntegerField(default=0)
    total_days = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, default='Productivity')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-streak', 'name']

    def __str__(self) -> str:
        return self.name

    def recalculate_metrics(self, today=None) -> None:
        today = today or timezone.localdate()
        completed_dates = set(
            self.completions.filter(completed=True).values_list('date', flat=True)
        )

        streak = 0
        cursor = today
        while cursor in completed_dates:
            streak += 1
            cursor -= timedelta(days=1)

        self.streak = streak
        self.total_days = len(completed_dates)


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['date']

    def __str__(self) -> str:
        return f'{self.habit.name} @ {self.date}'


class CalendarEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_events')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    title = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    duration = models.PositiveIntegerField(help_text='Duration in minutes')
    color = models.CharField(max_length=20, default='#403580')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self) -> str:
        return self.title


class FocusSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='focus_sessions')
    date = models.DateField()
    minutes = models.PositiveIntegerField()

    class Meta:
        ordering = ['date']

    def __str__(self) -> str:
        return f'{self.user} - {self.date} ({self.minutes}m)'
