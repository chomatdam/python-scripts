import calendar
import datetime

from slack_sdk.errors import SlackApiError
from .app_context import AppContext

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
    client_name: str,
    start_date: datetime.date,
    end_date: datetime.date,
) -> str:
    weekdays_count = count_days(start_date, end_date)
    worked_hours = weekdays_count * WORKHOURS_PER_DAY
    return "{}={}".format(client_name.upper(), worked_hours)


def build_weekly_report(client_name: str, current_date: datetime.date) -> str:
    monday = current_date - datetime.timedelta(current_date.weekday())
    friday_diff = FRIDAY_WEEK_INDEX - current_date.weekday()
    friday = current_date + datetime.timedelta(friday_diff)
    return format_report(client_name, monday, friday)


def build_monthly_report(client_name: str, current_date: datetime.date) -> str:
    start_date = datetime.date(current_date.year, current_date.month, 1)
    _, last_day_of_month = calendar.monthrange(current_date.year, current_date.month)
    end_date = datetime.date(current_date.year, current_date.month, last_day_of_month)
    return format_report(client_name, start_date, end_date)


def evaluate_messages_to_report(ctx: AppContext):
    # Messages to match
    weekly_message = "this week"
    monthly_message = "all hours for the month"

    # Get the latest messages from the channel
    response = ctx.get_slack_client().conversations_history(
        channel=ctx.get_slack_config().channel,
        limit=10,  # Limit to the 10 most recent messages
    )

    # Find the latest message from Joachim's bot
    message = None
    thread_ts = None
    if response["ok"]:
        for msg in response["messages"]:  # pyright: ignore
            # Pick latest message sent by Joachim
            if msg.get("user") != "USLACKBOT":
                continue
            # Don't post any report if we already posted in this thread
            if ctx.get_slack_config().user_id in msg.get("reply_users"):
                break

            msg_ts = msg.get("ts")
            report_date = datetime.datetime.fromtimestamp(float(msg_ts)).date()
            if report_date.day <= 10:
                _, last_day_prev_month = calendar.monthrange(
                    report_date.year, report_date.month - 1 or 12
                )
                report_date = datetime.date(
                    report_date.year if report_date.month > 1 else report_date.year - 1,
                    (report_date.month - 1) or 12,
                    last_day_prev_month,
                )

            thread_ts = msg.get("ts")
            if weekly_message in msg.get("text"):
                message = build_weekly_report(
                    client_name=ctx.get_company_client_name(),
                    current_date=report_date,
                )
            elif monthly_message in msg.get("text"):
                message = build_monthly_report(
                    client_name=ctx.get_company_client_name(),
                    current_date=report_date,
                )
            break

    # Reply in the thread
    if message is not None:
        print(message)
        try:
            ctx.get_slack_client().chat_postMessage(
                channel=ctx.get_slack_config().channel,
                text=message,
                mrkdwn=True,
                thread_ts=thread_ts,
            )
        except SlackApiError as error:
            print(f"Error fetching conversation history: {error.response}")
