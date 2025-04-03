# mf-auto-reg (Mastra Version)

An AI-powered tool, built with the [Mastra framework](https://mastra.ai/), that automatically registers ANA Pay and Rakuten Pay email notifications in MoneyForward.

## Features

- AI agent-based workflow automation using the Mastra framework
- Periodic monitoring and retrieval of ANA Pay and Rakuten Pay email notifications using Gmail API
- Extraction of transaction information (date, amount, store) from email content
- Transaction data deduplication management using Cloudflare D1
- User interaction through Slack
- Automated registration in MoneyForward using Playwright MCP in headless mode
- Declarative workflow definitions for maintainability
- Serverless execution environment leveraging GitHub Actions

## System Requirements

- GitHub account (for repository hosting and Actions)
- Node.js 20 or higher (check `.nvmrc` or `package.json` engines field)
- Google Cloud Project with Gmail API enabled (OAuth 2.0 Credentials)
- Cloudflare account with Workers and D1 enabled
- Slack workspace with a bot token having appropriate permissions
- MoneyForward account credentials

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/o3-ozono/mf-auto-reg.git
    cd mf-auto-reg
    ```

2.  **Install dependencies:** (This project uses npm, adjust if using pnpm or yarn)
    ```bash
    npm install
    ```

3.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.development .env
        ```
    *   Edit the `.env` file and fill in the required credentials and IDs. You will need:
        *   `GOOGLE_GENERATIVE_AI_API_KEY`: For the LLM provider (if using Google Gemini).
        *   `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`: For accessing Gmail API.
        *   `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`: For Slack notifications and interactions.
        *   `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`: For accessing Cloudflare API.
        *   `D1_DATABASE_ID`: Your Cloudflare D1 database ID.
        *   `MONEYFORWARD_EMAIL`, `MONEYFORWARD_PASSWORD`: For logging into MoneyForward.
        *   *(Add any other necessary variables based on implementation)*
    *   **Important:** Ensure the `.env` file is added to your `.gitignore` (it should be by default).

## Local Development

1.  **Start the Mastra development server:**
    ```bash
    npm run dev
    ```
2.  **Access the Mastra Dev UI:**
    *   Open your browser and navigate to `http://localhost:3000` (or the port specified in the console output).
    *   Here you can interact with your Mastra agents and workflows locally.

## Deployment & Execution (GitHub Actions)

- The primary execution method is via GitHub Actions workflows defined in the `.github/workflows/` directory (this directory might need to be created).
- **Secrets Configuration:** All sensitive credentials (API keys, passwords listed in `.env`) must be configured as encrypted secrets in your GitHub repository settings under `Settings > Secrets and variables > Actions`.
- **Workflow Trigger:** The workflow is typically triggered on a schedule (e.g., every 30 minutes) defined within the workflow YAML file.
- **Monitoring:** Execution logs and status can be monitored directly from the Actions tab in your GitHub repository.

## Project Structure Overview

- `src/mastra/`: Contains the core Mastra application logic.
  - `agents/`: Defines the AI agents used in the workflows.
  - `tools/`: Contains custom functions (tools) that agents can execute (e.g., interacting with Gmail, D1, Playwright).
  - `workflows/`: Defines the sequence and logic of automated tasks.
  - `index.ts`: Main entry point for Mastra configuration.
- `docs/`: Project documentation (like this README and architecture).
- `.github/workflows/`: GitHub Actions workflow definitions for automated execution.
- `.cursor/`: Cursor specific settings, including rules and MCP configuration.

## License

MIT 
