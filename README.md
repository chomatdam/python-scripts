# Python Scripts

## Work Time Off

### Context

Automates the generation and posting of weekly work time off reports to a specified Slack channel, summarizing work days
and hours for the given period.

### Environment Variables

| Variable                    | Description                                       | Scope                | Sensitive |
|-----------------------------|---------------------------------------------------|----------------------|:---------:|
| `PELOTECH_SLACK_USER_TOKEN` | Token used for Slack API authentication.          | Global               |     X     |
| `PELOTECH_CURRENT_CLIENT`   | Name of the current client.                       | Global               |           |
| `PELOTECH_SLACK_USER_ID`    | Slack user ID to be referenced in the report.     | Global               |           |
| `PELOTECH_SLACK_CHANNEL_ID` | Slack channel ID where the report will be posted. | Environment-specific |           |

### CLI Arguments

- `client_name` (positional) – The name of the client.
- `-c`, `--slack-channel` (required) – The Slack channel ID where the report will be posted.
- `-u`, `--slack-user-id` (required) – The Slack user ID associated with the report.
- `-t`, `--slack-token` (required) – The Slack token for authentication.

### Run

```shell
uv sync --all-extras --dev
uv run pytest tests
uv run worktimeoff 'client_name' -c 'slack_channel' -u 'slack_user_id' -t 'slack_token'
```
