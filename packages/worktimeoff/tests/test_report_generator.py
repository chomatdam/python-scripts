import datetime
from unittest import mock
from unittest.mock import patch, MagicMock

from worktimeoff.app_context import AppContext
from worktimeoff.report_generator import (
    get_date_range,
    count_days,
    format_report,
    build_weekly_report,
    build_monthly_report,
    evaluate_messages_to_report,
)

SLACK_CHANNEL = "C12345"
SLACK_USER_ID = "U12345"
CLIENT_NAME = "TestClient"


def test_get_date_range():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 3, 1)
    expected_output = [
        datetime.date(2023, 1, 1),
        datetime.date(2023, 2, 1),
        datetime.date(2023, 3, 1),
    ]
    assert get_date_range(start_date, end_date) == expected_output


def test_count_days():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 10)
    expected_count = 7  # Counting weekdays only
    assert count_days(start_date, end_date) == expected_count


def test_format_report():
    title = "Test Report"
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 10)
    expected_output = (
        "*Test Report*\n"
        f"From 01-01 to 01-10, <@{SLACK_USER_ID}> worked for a total "
        f"of 7 days (56 hours) at _{CLIENT_NAME.capitalize()}_."
    )
    assert (
        format_report(title, SLACK_USER_ID, CLIENT_NAME, start_date, end_date)
        == expected_output
    )


def test_build_weekly_report():
    current_date = datetime.date(2023, 1, 4)  # A Wednesday
    expected_output = (
        "*⏱️ Weekly Report*\n"
        f"From 01-02 to 01-06, <@{SLACK_USER_ID}> worked for a total "
        f"of 5 days (40 hours) at _{CLIENT_NAME.capitalize()}_."
    )
    assert (
        build_weekly_report(SLACK_USER_ID, CLIENT_NAME, current_date) == expected_output
    )


def test_build_monthly_report():
    current_date = datetime.date(2023, 1, 15)
    expected_output = (
        "*🗓️ Monthly Report*\n"
        f"From 01-01 to 01-31, <@{SLACK_USER_ID}> worked for a total "
        f"of 22 days (176 hours) at _{CLIENT_NAME.capitalize()}_."
    )
    assert (
        build_monthly_report(SLACK_USER_ID, CLIENT_NAME, current_date)
        == expected_output
    )


def test_evaluate_messages_to_report():
    report_date = datetime.date(2023, 1, 29)  # Last week of the month
    ctx = AppContext(SLACK_CHANNEL, SLACK_USER_ID, "SLACK_TOKEN", CLIENT_NAME)

    mock_slack_client = MagicMock()
    with patch.object(ctx, "slack_client", mock_slack_client):
        evaluate_messages_to_report(report_date, ctx)

    assert (
        mock_slack_client.chat_postMessage.called
    ), "Expected chat_postMessage to be called."
    assert (
        mock_slack_client.chat_postMessage.call_count == 2
    ), "Expected chat_postMessage to be called twice."

    calls = [
        mock.call(
            channel=SLACK_CHANNEL,
            text=f"*⏱️ Weekly Report*\nFrom 01-23 to 01-27, <@{SLACK_USER_ID}> worked for a total of 5 days (40 hours) at _{CLIENT_NAME.capitalize()}_.",
            mrkdwn=True,
        ),
        mock.call(
            channel=SLACK_CHANNEL,
            text=f"*🗓️ Monthly Report*\nFrom 01-01 to 01-31, <@{SLACK_USER_ID}> worked for a total of 22 days (176 hours) at _{CLIENT_NAME.capitalize()}_.",
            mrkdwn=True,
        ),
    ]
    mock_slack_client.chat_postMessage.assert_has_calls(calls, any_order=False)
