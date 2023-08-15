from dataclasses import dataclass

from slack_sdk import WebClient


@dataclass
class SlackConfig:
    channel: str
    user_id: str


class AppContext:
    def __init__(
        self,
        slack_channel: str,
        slack_user_id: str,
        slack_token: str,
        company_client_name: str,
    ):
        self.slack_client = WebClient(token=slack_token)
        self.slack_config = SlackConfig(channel=slack_channel, user_id=slack_user_id)
        self.company_client_name = company_client_name

    def get_slack_client(self) -> WebClient:
        return self.slack_client

    def get_slack_config(self) -> SlackConfig:
        return self.slack_config

    def get_company_client_name(self) -> str:
        return self.company_client_name
