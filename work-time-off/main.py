#!/usr/bin/env python3
import calendar
import datetime
import os
import sys
from dataclasses import dataclass

# import holidays
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slackClient = WebClient(token=os.environ["PELOTECH_SLACK_USER_TOKEN"])

WEEK_LENGTH = 7
FRIDAY_WEEK_INDEX = 4
WORKDAYS_PER_WEEK = 5
WORKHOURS_PER_DAY = 8


@dataclass
class Holiday:
    name: str
    datetime: datetime


@dataclass
class MonthlyReport:
    weekdays_count: int = 0
    # public_holidays: list[Holiday] = list


def get_date_range(start_date, end_date):
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


# def get_public_holidays(start_date, end_date):
#     date_range = get_date_range(start_date, end_date)
#     year_range = set(map(lambda date: date.year, date_range))
#     public_holidays = holidays.US(years=year_range).items()
#
#     selected_holidays = [Holiday(name=holiday[1], datetime=holiday[0]) for holiday in public_holidays if
#                          (holiday[0] >= start_date) & (holiday[0] <= end_date)]
#
#     return selected_holidays


def count_days(start_date, end_date):
    exclude = [5, 6]  # exclude Saturday (5) and Sunday (6)
    current_date = start_date
    count = 0
    while current_date <= end_date:
        if current_date.weekday() not in exclude:
            count += 1
        current_date += datetime.timedelta(days=1)

    return count


def build_report(start_date, end_date):
    report = MonthlyReport()

    weekdays_count = count_days(start_date, end_date)
    report.weekdays_count = weekdays_count

    # public_holidays = get_public_holidays(start_date, end_date)
    # report.public_holidays = public_holidays

    return report


def convert_worked_days_to_hours(report):
    return report.weekdays_count * WORKHOURS_PER_DAY
    # return (report.weekdays_count - len(report.public_holidays)) * WORKHOURS_PER_DAY


def format_report(title, slack_user_id, client_name, start_date, end_date):
    report = build_report(start_date, end_date)
    worked_hours = convert_worked_days_to_hours(report)
    lines = list()
    lines.append("*{}*".format(title))
    lines.append(
        "From {} to {}, <@{}> worked for a total of {} days ({} hours) at _{}_.".format(
            start_date.strftime("%m-%d"),
            end_date.strftime("%m-%d"),
            slack_user_id,
            report.weekdays_count,  # - len(report.public_holidays),
            worked_hours,
            client_name.capitalize(),
        )
    )

    # if len(report.public_holidays) > 0:
    #     names = "".join(["\n- {} ({})".format(off_day.name, off_day.datetime.strftime('%m/%d')) for off_day in
    #                      report.public_holidays])
    #     lines.append("🎉 FYI, we got day(s) off:{}".format(names))

    return "\n".join(lines)


def build_weekly_report(slack_user_id, client_name, current_date):
    monday = current_date - datetime.timedelta(current_date.weekday())
    friday_diff = FRIDAY_WEEK_INDEX - current_date.weekday()
    friday = current_date + datetime.timedelta(friday_diff)
    return format_report("⏱️ Weekly Report", slack_user_id, client_name, monday, friday)


def build_monthly_report(slack_user_id, client_name, current_date):
    start_date = datetime.date(current_date.year, current_date.month, 1)
    _, last_day_of_month = calendar.monthrange(current_date.year, current_date.month)
    end_date = datetime.date(current_date.year, current_date.month, last_day_of_month)
    return format_report("🗓️ Monthly Report", start_date, end_date)


print("--- Script started at {}".format(datetime.datetime.now()))

slack_channel = sys.argv[1]
slack_user_id = sys.argv[2]
current_client = sys.argv[3]

today = datetime.date.today()
messages = list()

weekly_message = build_weekly_report(slack_user_id, current_client, today)
messages.append(weekly_message)

is_last_week = today.day > (
    calendar.monthrange(today.year, today.month)[1] - WEEK_LENGTH
)
if is_last_week:
    monthly_message = build_monthly_report(slack_user_id, current_client, today)
    messages.append(monthly_message)

print("Messages to print:\n {}".format(messages))

for message in messages:
    try:
        response = slackClient.chat_postMessage(
            channel=slack_channel, text=message, mrkdwn=True
        )
    except SlackApiError as error:
        assert error.response["ok"] is False
        assert error.response["error"]
        print(f"Got an error: {error.response['error']}")

print("--- Script finished successfully at {}".format(datetime.datetime.now()))
sys.exit(0)
