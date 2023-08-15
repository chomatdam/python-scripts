import pytest
from unittest.mock import MagicMock

from worktimeoff import main
import argparse
import datetime

CLIENT_NAME = "CLIENT_NAME"
SLACK_CHANNEL = "SLACK_CHANNEL"
SLACK_USER_ID = "SLACK_USER_ID"
SLACK_TOKEN = "SLACK_TOKEN"


@pytest.fixture
def mock_parse_args(mocker):
    return mocker.patch("argparse.ArgumentParser.parse_args")


@pytest.fixture
def mock_app_context(mocker):
    return mocker.patch("worktimeoff.main.AppContext")


@pytest.fixture
def mock_evaluate_messages_to_report(mocker):
    return mocker.patch("worktimeoff.main.evaluate_messages_to_report")


def test_main(mock_parse_args, mock_app_context, mock_evaluate_messages_to_report):
    mock_parse_args.return_value = argparse.Namespace(
        slack_channel=SLACK_CHANNEL,
        slack_user_id=SLACK_USER_ID,
        slack_token=SLACK_TOKEN,
        client_name=CLIENT_NAME,
    )
    mock_app_context.return_value = MagicMock()

    main.main()

    mock_app_context.assert_called_once_with(
        slack_channel=SLACK_CHANNEL,
        slack_user_id=SLACK_USER_ID,
        slack_token=SLACK_TOKEN,
        company_client_name=CLIENT_NAME,
    )
    mock_evaluate_messages_to_report.assert_called_once_with(
        report_date=datetime.date.today(), ctx=mock_app_context()
    )
