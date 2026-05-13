from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import CalendarEvent, FocusSession, Habit, HabitCompletion, Task


User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo admin/user accounts and seed starter data.'

    def handle(self, *args, **options):
        today = timezone.localdate()

        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'User',
            },
        )
        admin_user.set_password('admin12345')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        demo_user, demo_created = User.objects.get_or_create(
            username='ibra',
            defaults={'first_name': 'Ibra', 'last_name': 'A.'},
        )
        demo_user.set_password('demo12345')
        demo_user.save()

        Task.objects.filter(user=demo_user).delete()
        Habit.objects.filter(user=demo_user).delete()
        CalendarEvent.objects.filter(user=demo_user).delete()
        FocusSession.objects.filter(user=demo_user).delete()

        tasks = [
            {
                'title': 'Design new landing page',
                'description': 'Create wireframes and high-fidelity mockups for the redesign',
                'priority': Task.Priority.HIGH,
                'status': Task.Status.IN_PROGRESS,
                'due_date': today,
                'tags': ['design', 'marketing'],
                'estimated_minutes': 120,
            },
            {
                'title': 'Review Q2 OKRs',
                'description': 'Analyze team performance metrics and adjust goals',
                'priority': Task.Priority.URGENT,
                'status': Task.Status.TODO,
                'due_date': today,
                'tags': ['management'],
                'estimated_minutes': 60,
            },
            {
                'title': 'Write weekly newsletter',
                'description': 'Summarize product updates and upcoming features',
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.TODO,
                'due_date': today,
                'tags': ['content'],
                'estimated_minutes': 45,
            },
            {
                'title': 'Fix authentication bug',
                'description': 'Users are being logged out after 10 minutes instead of 30',
                'priority': Task.Priority.URGENT,
                'status': Task.Status.DONE,
                'due_date': today - timedelta(days=1),
                'tags': ['engineering', 'bug'],
                'estimated_minutes': 90,
            },
            {
                'title': 'Update API documentation',
                'description': 'Add new endpoints to the public docs',
                'priority': Task.Priority.LOW,
                'status': Task.Status.DONE,
                'due_date': today - timedelta(days=1),
                'tags': ['engineering', 'docs'],
                'estimated_minutes': 30,
            },
            {
                'title': 'Prepare investor update',
                'description': 'Monthly metrics and roadmap for stakeholders',
                'priority': Task.Priority.HIGH,
                'status': Task.Status.TODO,
                'due_date': today + timedelta(days=1),
                'tags': ['business'],
                'estimated_minutes': 180,
            },
            {
                'title': 'User interviews - 3 sessions',
                'description': 'Talk to power users about the new task management flow',
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.IN_PROGRESS,
                'due_date': today + timedelta(days=1),
                'tags': ['research'],
                'estimated_minutes': 150,
            },
            {
                'title': 'Set up CI/CD pipeline',
                'description': 'Configure GitHub Actions for automated testing and deployment',
                'priority': Task.Priority.HIGH,
                'status': Task.Status.TODO,
                'due_date': today + timedelta(days=2),
                'tags': ['engineering', 'devops'],
                'estimated_minutes': 120,
            },
            {
                'title': 'Define brand guidelines',
                'description': 'Typography, color palette, and logo usage rules',
                'priority': Task.Priority.LOW,
                'status': Task.Status.DONE,
                'due_date': today - timedelta(days=2),
                'tags': ['design', 'brand'],
                'estimated_minutes': 240,
            },
            {
                'title': 'Onboard new designer',
                'description': 'Tool access, design system walkthrough, first-week plan',
                'priority': Task.Priority.MEDIUM,
                'status': Task.Status.TODO,
                'due_date': today + timedelta(days=2),
                'tags': ['hr'],
                'estimated_minutes': 90,
            },
        ]

        created_tasks = {
            task_data['title']: Task.objects.create(user=demo_user, **task_data)
            for task_data in tasks
        }

        habit_specs = [
            {
                'name': 'Morning Meditation',
                'icon': 'Heart',
                'color': '#403580',
                'category': 'Mindfulness',
                'weekly': [True, True, True, False, True, True, True],
                'history': 11,
            },
            {
                'name': 'Read 20 pages',
                'icon': 'BookOpen',
                'color': '#ea6634',
                'category': 'Learning',
                'weekly': [True, True, False, True, True, True, True],
                'history': 5,
            },
            {
                'name': 'Exercise',
                'icon': 'Activity',
                'color': '#10b981',
                'category': 'Health',
                'weekly': [False, True, True, True, True, True, False],
                'history': 2,
            },
            {
                'name': 'Deep Work - 2hrs',
                'icon': 'Target',
                'color': '#f59e0b',
                'category': 'Productivity',
                'weekly': [True, True, True, True, True, False, True],
                'history': 18,
            },
            {
                'name': 'No social media before 10am',
                'icon': 'SmartphoneOff',
                'color': '#6366f1',
                'category': 'Mindfulness',
                'weekly': [True, False, False, True, True, True, False],
                'history': 1,
            },
            {
                'name': 'Drink 2L of water',
                'icon': 'Droplets',
                'color': '#0ea5e9',
                'category': 'Health',
                'weekly': [True, True, True, True, False, True, True],
                'history': 6,
            },
        ]

        week_start = today - timedelta(days=today.weekday())
        for spec in habit_specs:
            habit = Habit.objects.create(
                user=demo_user,
                name=spec['name'],
                icon=spec['icon'],
                color=spec['color'],
                category=spec['category'],
            )
            for index, completed in enumerate(spec['weekly']):
                if completed:
                    HabitCompletion.objects.create(habit=habit, date=week_start + timedelta(days=index), completed=True)
            for offset in range(1, spec['history'] + 1):
                HabitCompletion.objects.get_or_create(
                    habit=habit,
                    date=week_start - timedelta(days=offset),
                    defaults={'completed': True},
                )
            habit.recalculate_metrics(today=today)
            habit.save(update_fields=['streak', 'total_days'])

        events = [
            {'title': 'Team standup', 'date': today - timedelta(days=2), 'time': time(9, 0), 'duration': 30, 'color': '#403580'},
            {'title': 'Define brand guidelines', 'date': today - timedelta(days=2), 'time': time(10, 0), 'duration': 240, 'color': '#ea6634', 'task': created_tasks['Define brand guidelines']},
            {'title': 'Fix auth bug', 'date': today - timedelta(days=1), 'time': time(9, 30), 'duration': 90, 'color': '#ef4444', 'task': created_tasks['Fix authentication bug']},
            {'title': '1:1 with team lead', 'date': today - timedelta(days=1), 'time': time(11, 0), 'duration': 60, 'color': '#403580'},
            {'title': 'Update API docs', 'date': today - timedelta(days=1), 'time': time(14, 0), 'duration': 30, 'color': '#10b981', 'task': created_tasks['Update API documentation']},
            {'title': 'Design landing page', 'date': today, 'time': time(9, 0), 'duration': 120, 'color': '#ea6634', 'task': created_tasks['Design new landing page']},
            {'title': 'Review Q2 OKRs', 'date': today, 'time': time(11, 30), 'duration': 60, 'color': '#f59e0b', 'task': created_tasks['Review Q2 OKRs']},
            {'title': 'Write newsletter', 'date': today, 'time': time(14, 0), 'duration': 45, 'color': '#6366f1', 'task': created_tasks['Write weekly newsletter']},
            {'title': 'Deep work session', 'date': today, 'time': time(15, 30), 'duration': 120, 'color': '#403580'},
            {'title': 'Investor call prep', 'date': today + timedelta(days=1), 'time': time(9, 0), 'duration': 60, 'color': '#f59e0b', 'task': created_tasks['Prepare investor update']},
            {'title': 'User interview #1', 'date': today + timedelta(days=1), 'time': time(10, 30), 'duration': 50, 'color': '#10b981', 'task': created_tasks['User interviews - 3 sessions']},
            {'title': 'User interview #2', 'date': today + timedelta(days=1), 'time': time(13, 0), 'duration': 50, 'color': '#10b981', 'task': created_tasks['User interviews - 3 sessions']},
            {'title': 'User interview #3', 'date': today + timedelta(days=1), 'time': time(15, 0), 'duration': 50, 'color': '#10b981', 'task': created_tasks['User interviews - 3 sessions']},
            {'title': 'CI/CD setup', 'date': today + timedelta(days=2), 'time': time(9, 0), 'duration': 120, 'color': '#403580', 'task': created_tasks['Set up CI/CD pipeline']},
            {'title': 'Onboard designer', 'date': today + timedelta(days=2), 'time': time(11, 30), 'duration': 90, 'color': '#ea6634', 'task': created_tasks['Onboard new designer']},
            {'title': 'Weekly retro', 'date': today + timedelta(days=2), 'time': time(16, 0), 'duration': 60, 'color': '#6366f1'},
        ]

        for event_data in events:
            CalendarEvent.objects.create(user=demo_user, **event_data)

        focus_minutes = [210, 120, 270, 180, 300, 90, 30]
        for index, minutes in enumerate(focus_minutes):
            FocusSession.objects.create(user=demo_user, date=week_start + timedelta(days=index), minutes=minutes)

        if admin_created:
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin12345'))
        else:
            self.stdout.write(self.style.WARNING('Updated admin password: admin / admin12345'))

        if demo_created:
            self.stdout.write(self.style.SUCCESS('Created demo user: ibra / demo12345'))
        else:
            self.stdout.write(self.style.WARNING('Updated demo password: ibra / demo12345'))

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
