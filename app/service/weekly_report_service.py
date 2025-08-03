"""Weekly report service for generating comprehensive time tracking reports."""

from datetime import date, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, func

from app.models import TimeEntry


class WeeklyReportService:
    """Service for generating weekly time tracking reports."""

    def __init__(self):
        """Initialize the weekly report service."""
        pass

    def parse_time_to_minutes(self, value) -> int:
        """Convert time value to minutes past midnight."""
        if value is None:
            return 0
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            if ':' in value:
                try:
                    hour, minute = map(int, value.split(':'))
                    return hour * 60 + minute
                except (ValueError, IndexError):
                    return 0
        return 0

    def format_time_for_display(self, value) -> str:
        """Convert time value to display format (e.g., '8:45 AM')."""
        minutes = self.parse_time_to_minutes(value)

        # Convert minutes past midnight to hours and minutes
        hours = minutes // 60
        mins = minutes % 60

        # Convert to 12-hour format
        display_hour = hours % 12
        if display_hour == 0:
            display_hour = 12

        am_pm = 'AM' if hours < 12 else 'PM'

        return f'{display_hour}:{mins:02d} {am_pm}'

    def format_duration(self, minutes: int) -> str:
        """Format duration in minutes to hours and minutes display."""
        if minutes < 0:
            return '0h 0m'

        hours = minutes // 60
        mins = minutes % 60

        if hours > 0:
            return f'{hours}h {mins}m'
        else:
            return f'{mins}m'

    def get_week_bounds(self, target_date: Optional[date] = None) -> tuple[date, date]:
        """Get the start (Sunday) and end (Saturday) dates for a week."""
        if target_date is None:
            target_date = date.today()

        # Calculate days since Sunday (0=Sunday, 1=Monday, etc.)
        days_since_sunday = (target_date.weekday() + 1) % 7

        # Get Sunday of this week
        sunday = target_date - timedelta(days=days_since_sunday)

        # Get Saturday of this week
        saturday = sunday + timedelta(days=6)

        return sunday, saturday

    def get_entries_for_period(self, start_date: date, end_date: date) -> List[TimeEntry]:
        """Get all time entries for the specified date range."""
        return (
            TimeEntry.query.filter(
                and_(func.date(TimeEntry.activity_date) >= start_date, func.date(TimeEntry.activity_date) <= end_date)
            )
            .order_by(TimeEntry.activity_date, TimeEntry.from_time)
            .all()
        )

    def calculate_daily_totals(self, entries: List[TimeEntry]) -> Dict[str, Dict]:
        """Calculate daily totals and statistics."""
        daily_totals = {}

        for entry in entries:
            entry_date = entry.activity_date.date()
            date_str = entry_date.strftime('%Y-%m-%d')

            if date_str not in daily_totals:
                daily_totals[date_str] = {
                    'date': entry_date,
                    'total_minutes': 0,
                    'activities': {},
                    'entries': [],
                    'first_start': None,
                    'last_end': None,
                }

            # Calculate duration
            from_minutes = self.parse_time_to_minutes(entry.from_time)
            to_minutes = self.parse_time_to_minutes(entry.to_time)
            duration = to_minutes - from_minutes

            # Track daily totals
            daily_totals[date_str]['total_minutes'] += duration

            # Track activity totals
            activity = entry.activity or 'Unknown'
            if activity not in daily_totals[date_str]['activities']:
                daily_totals[date_str]['activities'][activity] = 0
            daily_totals[date_str]['activities'][activity] += duration

            # Track first start and last end times
            if daily_totals[date_str]['first_start'] is None or from_minutes < daily_totals[date_str]['first_start']:
                daily_totals[date_str]['first_start'] = from_minutes

            if daily_totals[date_str]['last_end'] is None or to_minutes > daily_totals[date_str]['last_end']:
                daily_totals[date_str]['last_end'] = to_minutes

            # Add formatted entry
            daily_totals[date_str]['entries'].append(
                {
                    'id': entry.id,
                    'activity': activity,
                    'from_time': from_minutes,
                    'to_time': to_minutes,
                    'from_time_display': self.format_time_for_display(from_minutes),
                    'to_time_display': self.format_time_for_display(to_minutes),
                    'duration_minutes': duration,
                    'duration_display': self.format_duration(duration),
                    'time_out': bool(entry.time_out),
                }
            )

        return daily_totals

    def calculate_weekly_summary(self, daily_totals: Dict) -> Dict:
        """Calculate weekly summary statistics."""
        total_minutes = sum(day['total_minutes'] for day in daily_totals.values())
        total_days_worked = len([day for day in daily_totals.values() if day['total_minutes'] > 0])

        # Calculate activity totals across the week
        activity_totals = {}
        for day in daily_totals.values():
            for activity, minutes in day['activities'].items():
                if activity not in activity_totals:
                    activity_totals[activity] = 0
                activity_totals[activity] += minutes

        # Sort activities by total time
        sorted_activities = sorted(activity_totals.items(), key=lambda x: x[1], reverse=True)

        # Calculate average daily hours
        avg_daily_minutes = total_minutes / max(total_days_worked, 1)

        return {
            'total_minutes': total_minutes,
            'total_hours_display': self.format_duration(total_minutes),
            'total_days_worked': total_days_worked,
            'avg_daily_minutes': avg_daily_minutes,
            'avg_daily_display': self.format_duration(int(avg_daily_minutes)),
            'activity_totals': activity_totals,
            'sorted_activities': sorted_activities,
        }

    def generate_weekly_report(self, start_date: date, end_date: date) -> Dict:
        """Generate a comprehensive weekly report."""
        # Get all entries for the period
        entries = self.get_entries_for_period(start_date, end_date)

        # Calculate daily totals
        daily_totals = self.calculate_daily_totals(entries)

        # Calculate weekly summary
        weekly_summary = self.calculate_weekly_summary(daily_totals)

        # Generate a complete day list (including days with no entries)
        current_date = start_date
        complete_daily_data = []

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')

            if date_str in daily_totals:
                day_data = daily_totals[date_str].copy()
            else:
                day_data = {
                    'date': current_date,
                    'total_minutes': 0,
                    'activities': {},
                    'entries': [],
                    'first_start': None,
                    'last_end': None,
                }

            # Add formatted data
            day_data.update(
                {
                    'date_str': date_str,
                    'day_name': day_name,
                    'total_hours_display': self.format_duration(day_data['total_minutes']),
                    'first_start_display': (
                        self.format_time_for_display(day_data['first_start'])
                        if day_data['first_start'] is not None
                        else '-'
                    ),
                    'last_end_display': (
                        self.format_time_for_display(day_data['last_end']) if day_data['last_end'] is not None else '-'
                    ),
                }
            )

            complete_daily_data.append(day_data)
            current_date += timedelta(days=1)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'start_date_str': start_date.strftime('%Y-%m-%d'),
            'end_date_str': end_date.strftime('%Y-%m-%d'),
            'start_date_formatted': start_date.strftime('%B %d, %Y'),
            'end_date_formatted': end_date.strftime('%B %d, %Y'),
            'daily_data': complete_daily_data,
            'weekly_summary': weekly_summary,
            'total_entries': len(entries),
        }

    def get_default_week_dates(self) -> tuple[date, date]:
        """Get default start and end dates for the current week."""
        return self.get_week_bounds()
