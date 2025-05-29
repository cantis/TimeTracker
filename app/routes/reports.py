"""Routes for reports functionality."""

from datetime import date, timedelta

from flask import Blueprint, render_template, request

from app.models import TimeEntry, db  # Assuming TimeEntry is the model for time entries

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


def parse_time_to_minutes(value):
    """Convert 'HH:MM' string or int to minutes past midnight."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.isdigit():
            return int(value)
        if ':' in value:
            hour, minute = map(int, value.split(':'))
            return hour * 60 + minute
    raise ValueError(f'Unsupported time format: {value}')


@reports_bp.route('/weekly', methods=['GET', 'POST'])
def weekly_report():
    """Render the weekly report settings page or generate the report."""
    today = date.today()
    last_sunday = today - timedelta(days=today.weekday() + 1)
    last_saturday = last_sunday + timedelta(days=6)

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        entries = [
            {
                'date': entry.activity_date.strftime('%Y-%m-%d'),
                'activity': entry.activity,
                'from_time': entry.from_time,
                'to_time': entry.to_time,
                'duration': (parse_time_to_minutes(entry.to_time) - parse_time_to_minutes(entry.from_time)) // 60,
            }
            for entry in TimeEntry.query.filter(
                db.func.date(TimeEntry.activity_date) >= start_date, db.func.date(TimeEntry.activity_date) <= end_date
            )
            .order_by(TimeEntry.activity_date)
            .all()
        ]
        return render_template('reports/weekly_report.html', entries=entries, start_date=start_date, end_date=end_date)

    return render_template(
        'reports/weekly_settings.html',
        default_start_date=last_sunday.strftime('%Y-%m-%d'),
        default_end_date=last_saturday.strftime('%Y-%m-%d'),
    )
