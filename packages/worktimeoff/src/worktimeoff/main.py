import argparse
import datetime

from .report_generator import evaluate_messages_to_report
from .app_context import AppContext


def main():
    print("--- Script started at {}".format(datetime.datetime.now()))
    parser = argparse.ArgumentParser(description="Report work time off")
    parser.add_argument("client_name")  # positional argument
    parser.add_argument("-c", "--slack-channel", type=str, required=True)
    parser.add_argument("-u", "--slack-user-id", type=str, required=True)
    parser.add_argument("-t", "--slack-token", type=str, required=True)
    args = parser.parse_args()

    app_context = AppContext(
        slack_channel=args.slack_channel,
        slack_user_id=args.slack_user_id,
        slack_token=args.slack_token,
        company_client_name=args.client_name,
    )
    evaluate_messages_to_report(ctx=app_context)
    print("--- Script finished successfully at {}".format(datetime.datetime.now()))
