# mf-auto-reg

A Python tool that automatically retrieves ANA Pay email notifications from Gmail and registers them in MoneyForward.

## Features

- Periodic monitoring and retrieval of ANA Pay email notifications using Gmail API
- Extraction of transaction information (date, amount, store) from email content
- Transaction data deduplication management using Supabase
- User interaction through Slack
- Automated registration in MoneyForward using Browser Use
- Simple execution and management via command line interface

## System Requirements

- Python 3.11 or higher
- uv (package manager)
- Google account with Gmail API enabled
- Supabase account and project
- Slack workspace with a bot having appropriate permissions
- MoneyForward account

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/o3-ozono/mf-auto-reg.git
    ```

2. Create a virtual environment:

    ```bash
    uv venv
    ```

3. Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

4. Install dependencies:

    ```bash
    uv sync
    ```

5. Install in development mode:

    ```bash
    uv pip install -e .
    ```

## Setup

### 1. Google Cloud Platform Configuration

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 client credentials
4. Download credentials and save as `credentials.json`

### 2. Supabase Configuration

1. Create a project in [Supabase](https://supabase.com/)
2. Create the following table:

    ```sql
    create table transactions (
        id uuid default uuid_generate_v4() primary key,
        transaction_date timestamp with time zone,
        amount integer,
        store text,
        email_id text unique,
        status text,
        created_at timestamp with time zone default now(),
        updated_at timestamp with time zone default now()
    );
    ```

### 3. Slack Configuration

1. Create a new app in [Slack API](https://api.slack.com/apps)
2. Grant the following permissions:
   - `chat:write`
   - `reactions:read`
   - `channels:history`
3. Install the app to your workspace

### 4. Environment Variables

Create a `.env` file with the following information:

```env
# Gmail API Settings
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# Supabase Settings
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Slack Settings
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL_ID=your_channel_id

# MoneyForward Settings
MF_EMAIL=your_email
MF_PASSWORD=your_password
```

## Usage

### Basic Execution

```bash
# Run in daemon mode
mf-auto-reg run

# Run in foreground
mf-auto-reg run --no-daemon

# Run in debug mode
mf-auto-reg run --debug
```

### Detailed Configuration

Create a `config.yaml` file for detailed settings:

```yaml
gmail:
  search_query: "[ANA Pay] ご利用のお知らせ"
  max_results: 100
  poll_interval: 60  # seconds

moneyforward:
  account_id: "your_account_id"
  large_category: "Credit Card"
  middle_category: "ANA Pay"

slack:
  allowed_reactions:
    - "white_check_mark"  # Execute registration
    - "x"                 # Skip
```

### Slack Operations

1. The bot notifies Slack when new transactions are detected
2. Select operation with reactions:
   - ✅ (`white_check_mark`): Register in MoneyForward
   - ❌ (`x`): Skip
3. Notification is sent after registration is complete

## Development

### Running Tests

```bash
# Run all tests
uv run ./run_tests.py

# Generate coverage report
uv run coverage run -m unittest discover tests
uv run coverage report
```


## Troubleshooting

### Common Issues

1. Gmail API Authentication Error
   - Verify `credentials.json` is properly placed
   - Check OAuth consent screen settings

2. Slack Notifications Not Received
   - Verify bot token and channel ID
   - Ensure bot is invited to the channel

3. MoneyForward Registration Error
   - Verify login credentials
   - Check Browser Use settings

## License

MIT
