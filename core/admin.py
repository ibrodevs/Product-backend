from django.contrib import admin

from .models import CalendarEvent, FocusSession, Habit, HabitCompletion, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'due_date')
    list_filter = ('priority', 'status', 'due_date')
    search_fields = ('title', 'description', 'user__username')


class HabitCompletionInline(admin.TabularInline):
    model = HabitCompletion
    extra = 0


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'streak', 'total_days')
    list_filter = ('category',)
    search_fields = ('name', 'user__username')
    inlines = [HabitCompletionInline]


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date', 'time', 'duration')
    list_filter = ('date',)
    search_fields = ('title', 'user__username')


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'minutes')
    list_filter = ('date',)
    search_fields = ('user__username',)
