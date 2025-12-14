Initial setup

Create an API app entry at https://dev.freeagent.com

When run if they id and secret entries do not exist they will be prompted for.

Manual setup example on macOS

1. Set the client ID
security add-generic-password -a freeagent_client_id -s freeagent_api -w "your_client_id_here" -U

2. Set the client secret
security add-generic-password -a freeagent_client_secret -s freeagent_api -w "your_client_secret_here" -U


If you want to clear the oauth token from Keychain, you can run this once:
security delete-generic-password -a "oauth2_token" -s "freeagent_token"

