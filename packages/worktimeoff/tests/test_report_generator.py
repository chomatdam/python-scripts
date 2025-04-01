import datetime
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
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2023, 1, 10)
    expected_output = f"{CLIENT_NAME.upper()}=56"
    assert format_report(CLIENT_NAME, start_date, end_date) == expected_output


def test_build_weekly_report():
    current_date = datetime.date(2023, 1, 4)  # A Wednesday
    expected_output = f"{CLIENT_NAME.upper()}=40"
    assert build_weekly_report(CLIENT_NAME, current_date) == expected_output


def test_build_monthly_report():
    current_date = datetime.date(2023, 1, 15)
    expected_output = f"{CLIENT_NAME.upper()}=176"
    assert build_monthly_report(CLIENT_NAME, current_date) == expected_output


def test_evaluate_messages_to_report():
    ctx = AppContext(SLACK_CHANNEL, SLACK_USER_ID, "SLACK_TOKEN", CLIENT_NAME)

    # Create a mock Slack client
    mock_slack_client = MagicMock()

    # Mock the conversations_history response using the sample_payload
    import json

    sample_message = json.loads(sample_payload)
    mock_slack_client.conversations_history.return_value = {
        "ok": True,
        "messages": [sample_message],
    }

    # Patch the slack_client with our mock
    with patch.object(ctx, "slack_client", mock_slack_client):
        evaluate_messages_to_report(ctx)

    # Assert that chat_postMessage was called
    assert mock_slack_client.chat_postMessage.called, (
        "Expected chat_postMessage to be called."
    )

    # Assert the correct parameters were used
    mock_slack_client.chat_postMessage.assert_called_once_with(
        channel=SLACK_CHANNEL,
        text=f"{CLIENT_NAME.upper()}=168",
        mrkdwn=True,
        thread_ts="1743519625.368529",
    )


sample_payload = """
{
    "user": "USLACKBOT",
    "type": "message",
    "ts": "1743519625.368529",
    "bot_id": "B01",
    "text": "Reminder: Hiya<!here>! Please list a summary of all hours for the month by project - ie clientabc=120, client123(project1)=10, PTO/UPTO=10 as a thread to this message.",
    "team": "T02777WRC",
    "thread_ts": "1743519625.368529",
    "reply_count": 1,
    "reply_users_count": 1,
    "latest_reply": "1743519747.452949",
    "reply_users": ["U08ET982S2C"],
    "is_locked": false,
    "subscribed": false
}
"""
