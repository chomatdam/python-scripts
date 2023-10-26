# Python Scripts

Pdm is the package and dependency manager, `pdm install`.

## Weekly Report

### Initialization

```sh
JOB_FILE=com.pelotech.worktimeoff.plist

# Validate the plist format and syntax is valid XML
plutil -lint $PWD/$JOB_FILE

# Save the job to your user launch agents folder
cp $PWD/$JOB_FILE ~/Library/LaunchAgents/$JOB_FILE

# Load and confirm the job is loaded
launchctl load ~/Library/LaunchAgents/$JOB_FILE
launchctl list | grep pelotech

# Start manually to validate the script execution
launchctl start com.pelotech.worktimeoff

# Debug if needed
log show | grep pelotech # System logs
tail -f $PWD/logs/out.log # Application logs

# Once script validated, stop it
launchctl stop com.pelotech.worktimeoff
launchctl unload ~/Library/LaunchAgents/$JOB_FILE
```
### Environment variables

#### Slack
```sh
# Temporary
launchctl setenv PELOTECH_SLACK_USER_TOKEN $PELOTECH_SLACK_USER_TOKEN
launchctl getenv PELOTECH_SLACK_USER_TOKEN
# Permanent
vi /etc/launchd.conf
setenv PELOTECH_SLACK_USER_TOKEN $PELOTECH_SLACK_USER_TOKEN
```


### Changing parameters

| Type                                 | Location                                   |
|--------------------------------------|--------------------------------------------|
| Debug / Manual Execution             | .plist file - uncomment `KeepAlive`        |
| Schedule (reporting a different day) | .plist file - edit `StartCalendarInterval` |
| Company name                         | Python script - variable `CURRENT_CLIENT`  |

Effects are applied instantly when changing the Python script. Any change to the .plist requires to copy/unload and load
the new .plist file
