import calendar
import datetime

from slack_sdk.errors import SlackApiError
from worktimeoff.app_context import AppContext

WEEK_LENGTH = 7
FRIDAY_WEEK_INDEX = 4
WORKDAYS_PER_WEEK = 5
WORKHOURS_PER_DAY = 8


def get_date_range(
    start_date: datetime.date, end_date: datetime.date
) -> list[datetime.date]:
    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)

        # Increment month by 1
        month = current_date.month
        year = current_date.year
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

        current_date = current_date.replace(year=year, month=month)

    return dates


def count_days(start_date: datetime.date, end_date: datetime.date) -> int:
    exclude = [5, 6]  # exclude Saturday (5) and Sunday (6)
    current_date = start_date
    count = 0
    while current_date <= end_date:
        if current_date.weekday() not in exclude:
            count += 1
        current_date += datetime.timedelta(days=1)

    return count


def format_report(
    title: str,
    user_id: str,
    client_name: str,
    start_date: datetime.date,
    end_date: datetime.date,
) -> str:
    weekdays_count = count_days(start_date, end_date)
    worked_hours = weekdays_count * WORKHOURS_PER_DAY
    lines = list()
    lines.append("*{}*".format(title))
    lines.append(
        "From {} to {}, <@{}> worked for a total of {} days ({} hours) at _{}_.".format(
            start_date.strftime("%m-%d"),
            end_date.strftime("%m-%d"),
            user_id,
            weekdays_count,
            worked_hours,
            client_name.capitalize(),
        )
    )

    return "\n".join(lines)


def build_weekly_report(
    user_id: str, client_name: str, current_date: datetime.date
) -> str:
    monday = current_date - datetime.timedelta(current_date.weekday())
    friday_diff = FRIDAY_WEEK_INDEX - current_date.weekday()
    friday = current_date + datetime.timedelta(friday_diff)
    return format_report("⏱️ Weekly Report", user_id, client_name, monday, friday)


def build_monthly_report(
    user_id: str, client_name: str, current_date: datetime.date
) -> str:
    start_date = datetime.date(current_date.year, current_date.month, 1)
    _, last_day_of_month = calendar.monthrange(current_date.year, current_date.month)
    end_date = datetime.date(current_date.year, current_date.month, last_day_of_month)
    return format_report("🗓️ Monthly Report", user_id, client_name, start_date, end_date)


def evaluate_messages_to_report(report_date: datetime.date, ctx: AppContext):
    messages = list()

    weekly_message = build_weekly_report(
        user_id=ctx.get_slack_config().user_id,
        client_name=ctx.get_company_client_name(),
        current_date=report_date,
    )
    messages.append(weekly_message)

    is_last_week = report_date.day > (
        calendar.monthrange(report_date.year, report_date.month)[1] - WEEK_LENGTH
    )
    if is_last_week:
        monthly_message = build_monthly_report(
            user_id=ctx.get_slack_config().user_id,
            client_name=ctx.get_company_client_name(),
            current_date=report_date,
        )
        messages.append(monthly_message)

    print("Messages to print:\n {}".format(messages))

    for message in messages:
        try:
            ctx.get_slack_client().chat_postMessage(
                channel=ctx.get_slack_config().channel, text=message, mrkdwn=True
            )
        except SlackApiError as error:
            print(f"Got an error: {error.response['error']}")
