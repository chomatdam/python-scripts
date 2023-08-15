#!/usr/bin/env python3
import calendar
import datetime
import subprocess
import sys
from dataclasses import dataclass

import holidays

KEYBASE_CHANNEL = 'chomatdam'
CURRENT_CLIENT = 'cinch'
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
    public_holidays: list[Holiday] = list


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


def get_public_holidays(start_date, end_date):
    date_range = get_date_range(start_date, end_date)
    year_range = set(map(lambda date: date.year, date_range))
    public_holidays = holidays.US(years=year_range).items()

    selected_holidays = [Holiday(name=holiday[1], datetime=holiday[0]) for holiday in public_holidays if
                         (holiday[0] >= start_date) & (holiday[0] <= end_date)]

    return selected_holidays


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

    public_holidays = get_public_holidays(start_date, end_date)
    report.public_holidays = public_holidays

    return report


def convert_worked_days_to_hours(report):
    return (report.weekdays_count - len(report.public_holidays)) * WORKHOURS_PER_DAY


def format_report(title, start_date, end_date):
    report = build_report(start_date, end_date)
    worked_hours = convert_worked_days_to_hours(report)
    lines = list()
    lines.append("[ {} ]".format(title))
    lines.append("💪 From {} to {}, I worked for a total of {} days ({} hours) at '{}'.".format(start_date,
                                                                                               end_date,
                                                                                               report.weekdays_count - len(
                                                                                                   report.public_holidays),
                                                                                               worked_hours,
                                                                                               CURRENT_CLIENT.capitalize()))
    if len(report.public_holidays) > 0:
        names = "".join(["\n- {} ({})".format(off_day.name, off_day.datetime.strftime('%m/%d')) for off_day in
                         report.public_holidays])
        lines.append("🎉 FYI, we got days off:{}".format(names))

    return "\n".join(lines)


def build_weekly_report(current_date):
    monday = current_date - datetime.timedelta(current_date.weekday())
    friday_diff = FRIDAY_WEEK_INDEX - current_date.weekday()
    friday = current_date + datetime.timedelta(friday_diff)
    return format_report("Weekly Report", monday, friday)


def build_monthly_report(current_date):
    start_date = datetime.date(current_date.year, current_date.month, 1)
    _, last_day_of_month = calendar.monthrange(current_date.year, current_date.month)
    end_date = datetime.date(current_date.year, current_date.month, last_day_of_month)
    return format_report("Monthly Report", start_date, end_date)


print("--- Script started at {}".format(datetime.datetime.now()))

today = datetime.date.today()
messages = list()

weekly_message = build_weekly_report(today)
messages.append(weekly_message)

is_last_week = today.day > (calendar.monthrange(today.year, today.month)[1] - WEEK_LENGTH)
if is_last_week:
    monthly_message = build_monthly_report(today)
    messages.append(monthly_message)

print("Messages to print:\n {}".format(messages))

for message in messages:
    args = ['zsh', '-c', "/Applications/Keybase.app/Contents/SharedSupport/bin/keybase chat send \"{}\" \"{}\"".format(KEYBASE_CHANNEL, message)]
    process = subprocess.run(args, capture_output=True, text=True)
    print(process.stdout)

print("--- Script finished successfully at {}".format(datetime.datetime.now()))
sys.exit(0)
