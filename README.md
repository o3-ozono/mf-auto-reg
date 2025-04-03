# mf-auto-reg (Mastra Version)

An AI-powered tool that automatically registers ANA Pay and Rakuten Pay email notifications in MoneyForward.

## Features

- AI agent-based workflow automation using the Mastra framework
- Periodic monitoring and retrieval of ANA Pay and Rakuten Pay email notifications using Gmail API
- Extraction of transaction information (date, amount, store) from email content
- Transaction data deduplication management using Cloudflare D1
- User interaction through Slack
- Automated registration in MoneyForward using Playwright MCP in headless mode
- Easy maintenance through declarative workflow definitions
- Serverless execution through GitHub Actions

## System Requirements

- GitHub account with Actions enabled
- Node.js 18 or higher (for local development)
- Google account with Gmail API enabled
- Cloudflare account with Workers and D1 enabled
- Slack workspace with a bot having appropriate permissions
- MoneyForward account

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/o3-ozono/mf-auto-reg.git
    ```

2. Install dependencies:

    ```bash
    # Using npm
    npm install

    # Using yarn
    yarn install
    ```

## Setup

### 1. Google Cloud Platform Configuration

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 client credentials
4. Download credentials and save as `credentials.json`

### 2. Cloudflare D1 Configuration

1. Create a D1 database in your Cloudflare dashboard
2. Set up the following table:

    ```sql
    CREATE TABLE transactions (
        id TEXT PRIMARY KEY,
        transaction_date TIMESTAMP,
        amount INTEGER,
        store TEXT,
        email_id TEXT UNIQUE,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ```

3. Configure Cloudflare Workers to access your D1 database

### 3. Slack Configuration

1. Create a new app in [Slack API](https://api.slack.com/apps)
2. Grant the following permissions:
   - `chat:write`
   - `reactions:read`
   - `channels:history`
3. Install the app to your workspace

### 4. GitHub Actions Configuration

1. Create a workflow file at `.github/workflows/email-processor.yml`:

    ```yaml
    name: Process Emails
    
    on:
      # Run every 10 minutes
      schedule:
        - cron: '*/10 * * * *'
      
      # Allow manual triggers
      workflow_dispatch:
    
    jobs:
      process:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          
          - name: Setup Node.js
            uses: actions/setup-node@v3
            with:
              node-version: '18'
              cache: 'npm'
          
          - name: Install dependencies
            run: npm ci
          
          - name: Setup Playwright
            run: npx playwright install --with-deps chromium
          
          - name: Start Playwright MCP in headless mode
            run: |
              npx @playwright/mcp@latest --headless --port 8931 &
              sleep 5
          
          - name: Run Mastra workflow
            env:
              # Environment variables from GitHub Secrets
              GMAIL_CLIENT_ID: ${{ secrets.GMAIL_CLIENT_ID }}
              GMAIL_CLIENT_SECRET: ${{ secrets.GMAIL_CLIENT_SECRET }}
              GMAIL_REFRESH_TOKEN: ${{ secrets.GMAIL_REFRESH_TOKEN }}
              CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
              CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
              D1_DATABASE_NAME: ${{ secrets.D1_DATABASE_NAME }}
              SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
              SLACK_CHANNEL_ID: ${{ secrets.SLACK_CHANNEL_ID }}
              MF_EMAIL: ${{ secrets.MF_EMAIL }}
              MF_PASSWORD: ${{ secrets.MF_PASSWORD }}
              PLAYWRIGHT_MCP_URL: "http://localhost:8931/sse"
            run: node src/index.js
    ```

2. Add all required secrets in your GitHub repository:
   - Go to your repository's Settings
   - Navigate to Secrets and Variables > Actions
   - Add all the required secrets (GMAIL_CLIENT_ID, etc.)

### 5. Environment Variables

Create a `.env` file with the following information (for local development):

```env
# Gmail API Settings
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# Cloudflare Settings
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token
D1_DATABASE_NAME=your_database_name

# Slack Settings
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL_ID=your_channel_id

# MoneyForward Settings
MF_EMAIL=your_email
MF_PASSWORD=your_password
```

### 6. Playwright MCP Configuration

Create a `mcp-config.json` file with the following content:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless"
      ]
    }
  }
}
```

## Usage

### Local Execution (for development)

```bash
# Run in development mode
npm run dev

# Debug mode
npm run start:debug
```

### GitHub Actions Execution

The workflow will automatically run based on the schedule defined in the workflow file. You can also manually trigger the workflow from the "Actions" tab in your GitHub repository.

### Detailed Configuration

Define your workflow in the `workflow.yaml` file:

```yaml
name: "MoneyForward Auto Registration"
description: "Workflow to automatically register ANA Pay and Rakuten Pay email notifications in MoneyForward"

nodes:
  - name: "EmailPolling"
    type: "GmailPoller"
    config:
      searchQueries:
        - "[ANA Pay] ご利用のお知らせ"
        - "[楽天ペイ] ご利用のお知らせ"
      maxResults: 100
      pollInterval: 60000
    next: "EmailParser"

  - name: "EmailParser"
    type: "ConditionalRouter"
    config:
      routes:
        - condition: "email.subject.includes('ANA Pay')"
          next: "ANAPayParser"
        - condition: "email.subject.includes('楽天ペイ')"
          next: "RakutenPayParser"
        - default: "End"

  - name: "ANAPayParser"
    type: "EmailContentParser"
    config:
      paymentService: "ANAPay"
    next: "DuplicateCheck"

  - name: "RakutenPayParser"
    type: "EmailContentParser"
    config:
      paymentService: "RakutenPay"
    next: "DuplicateCheck"

  - name: "DuplicateCheck"
    type: "CloudflareD1Query"
    config:
      operation: "checkDuplicate"
      table: "transactions"
      uniqueField: "email_id"
    next:
      routes:
        - condition: "result.isDuplicate"
          next: "End"
        - default: "StoreTransaction"

  - name: "StoreTransaction"
    type: "CloudflareD1Query"
    config:
      operation: "insert"
      table: "transactions"
    next: "SlackNotification"

  - name: "SlackNotification"
    type: "SlackSender"
    config:
      messageTemplate: "transaction-notification.md"
    next: "WaitForReaction"

  - name: "WaitForReaction"
    type: "SlackReactionWatcher"
    config:
      allowedReactions:
        - "white_check_mark"
        - "x"
      timeout: 86400000  # 24 hours
    next:
      routes:
        - condition: "reaction === 'white_check_mark'"
          next: "MoneyForwardRegistration"
        - condition: "reaction === 'x'"
          next: "SkipRegistration"
        - default: "End"

  - name: "MoneyForwardRegistration"
    type: "PlaywrightMCP"
    config:
      mode: "snapshot"
      operationTemplate: "moneyforward-registration.yaml"
    next: "UpdateTransactionStatus"

  - name: "UpdateTransactionStatus"
    type: "CloudflareD1Query"
    config:
      operation: "update"
      table: "transactions"
      updateField: "status"
      value: "registered"
    next: "RegistrationCompletionNotification"

  - name: "RegistrationCompletionNotification"
    type: "SlackSender"
    config:
      messageTemplate: "registration-complete.md"
    next: "End"

  - name: "SkipRegistration"
    type: "CloudflareD1Query"
    config:
      operation: "update"
      table: "transactions"
      updateField: "status"
      value: "skipped"
    next: "End"

  - name: "End"
    type: "EndWorkflow"
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
npm test

# Run with coverage
npm run test:coverage
```

## Custom Node Development

You can develop custom nodes by extending the Mastra framework:

```typescript
import { Node, NodeConfig } from 'mastra';

interface EmailParserConfig extends NodeConfig {
  paymentService: 'ANAPay' | 'RakutenPay';
}

export class EmailContentParser extends Node<EmailParserConfig> {
  async execute(context: any) {
    const { email } = context;
    const { paymentService } = this.config;
    
    let transaction;
    
    if (paymentService === 'ANAPay') {
      transaction = this.parseANAPayEmail(email);
    } else if (paymentService === 'RakutenPay') {
      transaction = this.parseRakutenPayEmail(email);
    }
    
    return { ...context, transaction };
  }
  
  private parseANAPayEmail(email: any) {
    // ANA email parsing logic
  }
  
  private parseRakutenPayEmail(email: any) {
    // Rakuten Pay email parsing logic
  }
}
```

## Benefits of GitHub Actions

- **Zero Infrastructure**: No need to maintain dedicated servers
- **Cost Efficiency**: Free tier includes 2,000 minutes per month for private repositories
- **Simplicity**: Built-in scheduling and secret management
- **Reliability**: Managed execution environment with logs and notifications
- **Integration**: Seamless integration with your GitHub repository

## License

MIT 
