"""Routes for reports functionality."""

from datetime import date

from flask import Blueprint, render_template, request

from app.service.weekly_report_service import WeeklyReportService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/weekly', methods=['GET', 'POST'])
def weekly_report():
    """Render the weekly report settings page or generate the report."""
    service = WeeklyReportService()

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        try:
            if start_date_str and end_date_str:
                start_date = date.fromisoformat(start_date_str)
                end_date = date.fromisoformat(end_date_str)
            else:
                # If date strings are missing, use default week
                start_date, end_date = service.get_default_week_dates()
        except (ValueError, TypeError):
            # If date parsing fails, use default week
            start_date, end_date = service.get_default_week_dates()

        # Generate the report
        report_data = service.generate_weekly_report(start_date, end_date)

        return render_template('reports/weekly_report.html', **report_data)

    # GET request - show the settings page
    default_start_date, default_end_date = service.get_default_week_dates()

    return render_template(
        'reports/weekly_settings.html',
        default_start_date=default_start_date.strftime('%Y-%m-%d'),
        default_end_date=default_end_date.strftime('%Y-%m-%d'),
    )
