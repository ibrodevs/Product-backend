from calendar import month_abbr
from datetime import date, timedelta

from django.db.models import Sum
from django.utils import timezone

from .models import FocusSession, Habit, Task
from .serializers import HabitSerializer, TaskSerializer, UserSerializer


CATEGORY_COLORS = ['#403580', '#ea6634', '#10b981', '#f59e0b', '#6366f1', '#0ea5e9']
DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def get_week_start(target_date: date) -> date:
    return target_date - timedelta(days=target_date.weekday())


def get_week_dates(target_date: date) -> list[date]:
    week_start = get_week_start(target_date)
    return [week_start + timedelta(days=index) for index in range(7)]


def calculate_change(current_value: float, previous_value: float) -> int:
    if previous_value == 0:
        return 100 if current_value > 0 else 0
    return round(((current_value - previous_value) / previous_value) * 100)


def serialize_weekly_tasks(user, target_date: date) -> list[dict]:
    data = []
    for day in get_week_dates(target_date):
        daily_tasks = Task.objects.filter(user=user, due_date=day)
        total = daily_tasks.count()
        completed = daily_tasks.filter(status=Task.Status.DONE).count()
        data.append(
            {
                'day': DAY_NAMES[day.weekday()],
                'date': day.isoformat(),
                'completed': completed,
                'total': total,
            }
        )
    return data


def serialize_focus_time(user, target_date: date) -> list[dict]:
    sessions = FocusSession.objects.filter(
        user=user,
        date__gte=get_week_start(target_date),
        date__lte=get_week_start(target_date) + timedelta(days=6),
    )
    minutes_by_date = {
        row['date']: row['minutes']
        for row in sessions.values('date').annotate(minutes=Sum('minutes'))
    }
    return [
        {
            'day': DAY_NAMES[day.weekday()],
            'hours': round((minutes_by_date.get(day, 0) or 0) / 60, 1),
        }
        for day in get_week_dates(target_date)
    ]


def serialize_category_data(user) -> list[dict]:
    tag_counts = {}
    for task in Task.objects.filter(user=user):
        if not task.tags:
            continue
        category = str(task.tags[0]).strip().title()
        if not category:
            continue
        tag_counts[category] = tag_counts.get(category, 0) + 1

    sorted_items = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    return [
        {
            'category': category,
            'count': count,
            'color': CATEGORY_COLORS[index % len(CATEGORY_COLORS)],
        }
        for index, (category, count) in enumerate(sorted_items)
    ]


def serialize_monthly_stats(user, target_date: date) -> list[dict]:
    months = []
    year = target_date.year
    month = target_date.month
    for _ in range(5):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    months.reverse()

    results = []
    for year, month in months:
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(year, month + 1, 1) - timedelta(days=1)
        tasks = Task.objects.filter(user=user, due_date__gte=month_start, due_date__lte=month_end).count()
        habits = Habit.objects.filter(
            user=user,
            completions__date__gte=month_start,
            completions__date__lte=month_end,
            completions__completed=True,
        ).count()
        results.append({'month': month_abbr[month], 'tasks': tasks, 'habits': habits})
    return results


def build_dashboard_payload(user, request) -> dict:
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    weekly_data = serialize_weekly_tasks(user, today)
    today_tasks_qs = Task.objects.filter(user=user, due_date=today).order_by('created_at')
    yesterday_tasks = Task.objects.filter(user=user, due_date=yesterday)
    completed_today = today_tasks_qs.filter(status=Task.Status.DONE).count()
    total_today = today_tasks_qs.count()
    completed_yesterday = yesterday_tasks.filter(status=Task.Status.DONE).count()

    focus_today_minutes = FocusSession.objects.filter(user=user, date=today).aggregate(total=Sum('minutes'))['total'] or 0
    focus_yesterday_minutes = FocusSession.objects.filter(user=user, date=yesterday).aggregate(total=Sum('minutes'))['total'] or 0

    habits_qs = Habit.objects.filter(user=user)
    max_habit_streak = habits_qs.order_by('-streak').first().streak if habits_qs.exists() else 0

    week_completed = sum(item['completed'] for item in weekly_data)
    week_total = sum(item['total'] for item in weekly_data)
    previous_week_data = serialize_weekly_tasks(user, today - timedelta(days=7))
    prev_completed = sum(item['completed'] for item in previous_week_data)
    prev_total = sum(item['total'] for item in previous_week_data)

    focus_hours = round(focus_today_minutes / 60, 1)
    completion_rate = round((week_completed / week_total) * 100) if week_total else 0
    previous_completion_rate = round((prev_completed / prev_total) * 100) if prev_total else 0

    priority_order = {
        Task.Priority.URGENT: 0,
        Task.Priority.HIGH: 1,
        Task.Priority.MEDIUM: 2,
        Task.Priority.LOW: 3,
    }
    open_tasks = list(Task.objects.filter(user=user).exclude(status=Task.Status.DONE).order_by('due_date', 'created_at'))
    focus_task = sorted(
        open_tasks,
        key=lambda task: (
            task.due_date != today,
            priority_order[task.priority],
            task.due_date,
            task.created_at,
        ),
    )[0] if open_tasks else None

    current_hour = timezone.localtime().hour
    if current_hour < 12:
        greeting = 'Good morning'
    elif current_hour < 18:
        greeting = 'Good afternoon'
    else:
        greeting = 'Good evening'

    return {
        'profile': UserSerializer(user).data,
        'today': today.isoformat(),
        'todayLabel': today.strftime('%A, %B %d, %Y'),
        'greeting': greeting,
        'tasksRemaining': max(total_today - completed_today, 0),
        'stats': {
            'tasksToday': {
                'completed': completed_today,
                'total': total_today,
                'change': calculate_change(completed_today, completed_yesterday),
            },
            'focusHours': {
                'value': focus_hours,
                'change': calculate_change(focus_today_minutes, focus_yesterday_minutes),
            },
            'bestStreak': {
                'value': max_habit_streak,
                'change': 0,
            },
            'completionRate': {
                'value': completion_rate,
                'change': calculate_change(completion_rate, previous_completion_rate),
            },
        },
        'focusTask': TaskSerializer(focus_task).data if focus_task else None,
        'todayTasks': TaskSerializer(today_tasks_qs[:4], many=True).data,
        'weeklyOverview': weekly_data,
        'topHabits': HabitSerializer(habits_qs.order_by('-streak')[:3], many=True, context={'request': request}).data,
    }


def build_analytics_payload(user) -> dict:
    today = timezone.localdate()
    weekly_data = serialize_weekly_tasks(user, today)
    focus_time_data = serialize_focus_time(user, today)
    category_data = serialize_category_data(user)
    monthly_stats = serialize_monthly_stats(user, today)

    total_completed = sum(item['completed'] for item in weekly_data)
    total_tasks = sum(item['total'] for item in weekly_data)
    total_focus_hours = round(sum(item['hours'] for item in focus_time_data), 1)

    habits_qs = Habit.objects.filter(user=user)
    habit_serialized = HabitSerializer(habits_qs, many=True, context={'request': None}).data
    habit_consistency = round(
        sum(sum(1 for day in habit['completedDays'] if day) / 7 for habit in habit_serialized) / len(habit_serialized) * 100
    ) if habit_serialized else 0

    previous_week_data = serialize_weekly_tasks(user, today - timedelta(days=7))
    previous_focus_data = serialize_focus_time(user, today - timedelta(days=7))
    prev_completed = sum(item['completed'] for item in previous_week_data)
    prev_total = sum(item['total'] for item in previous_week_data)
    prev_completion_rate = round((prev_completed / prev_total) * 100) if prev_total else 0
    current_completion_rate = round((total_completed / total_tasks) * 100) if total_tasks else 0

    previous_consistency = 0
    if habits_qs.exists():
        previous_week_dates = [date.fromisoformat(item['date']) for item in previous_week_data]
        for habit in habits_qs:
            completed = habit.completions.filter(date__in=previous_week_dates, completed=True).count()
            previous_consistency += completed / 7
        previous_consistency = round(previous_consistency / habits_qs.count() * 100)

    week_start = get_week_start(today)
    week_end = week_start + timedelta(days=6)

    return {
        'periodLabel': f'{week_start.strftime("%b %d")} - {week_end.strftime("%d, %Y")}',
        'totalCompleted': total_completed,
        'totalTasks': total_tasks,
        'totalFocusHours': total_focus_hours,
        'habitConsistency': habit_consistency,
        'changes': {
            'tasksCompleted': calculate_change(total_completed, prev_completed),
            'completionRate': calculate_change(current_completion_rate, prev_completion_rate),
            'focusHours': calculate_change(sum(item['hours'] for item in focus_time_data), sum(item['hours'] for item in previous_focus_data)),
            'habitConsistency': calculate_change(habit_consistency, previous_consistency),
        },
        'weeklyTaskData': weekly_data,
        'focusTimeData': focus_time_data,
        'categoryData': category_data,
        'monthlyStats': monthly_stats,
    }
