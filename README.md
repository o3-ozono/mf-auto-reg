# mf-auto-reg

An AI-powered tool, built with the [Mastra framework](https://mastra.ai/), that automatically registers ANA Pay and Rakuten Pay email notifications into MoneyForward ME.

## Overview

This project leverages the Mastra framework to create an automated workflow that:

1.  Periodically checks a specified Gmail account for new payment notification emails (ANA Pay, Rakuten Pay).
2.  Parses these emails using custom tools to extract transaction details (date, amount, store).
3.  Checks for duplicates and stores transaction information in a Cloudflare D1 database.
4.  (Optional) Interacts with users via Slack for notifications or confirmations.
5.  Uses Playwright via Mastra's Playwright Control Plane (MCP) to automatically log in to MoneyForward ME and register the transaction.

## Core Technologies

-   **Workflow Automation**: [Mastra Framework](https://mastra.ai/)
-   **Language**: TypeScript
-   **Database**: Cloudflare D1
-   **Web Automation**: Playwright & Playwright MCP
-   **Testing**: Jest (Unit & Integration), Playwright (E2E)
-   **Local Development**: Miniflare (for local D1 emulation), Wrangler CLI
-   **Deployment**: GitHub Actions

## Features

-   AI agent-based workflow automation using Mastra.
-   Gmail API integration for fetching emails.
-   Custom parsers for extracting data from specific email formats.
-   Transaction data storage and deduplication using Cloudflare D1.
-   Automated browser interaction with MoneyForward ME via Playwright MCP.
-   Declarative workflow definitions in YAML (within Mastra).
-   Serverless execution potential via Cloudflare Workers or scheduled GitHub Actions.
-   (Optional) Slack integration for notifications.

## System Requirements

-   GitHub account (for repository hosting and Actions).
-   Node.js 22 or higher (refer to `.nvmrc` or `package.json` engines field).
-   npm (Node Package Manager).
-   Google Cloud Project with Gmail API enabled (OAuth 2.0 Credentials).
-   Cloudflare account with Workers and D1 enabled.
-   (Optional) Slack workspace and bot token.
-   MoneyForward ME account credentials.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/o3-ozono/mf-auto-reg.git
    cd mf-auto-reg
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.development .env
        ```
    *   Edit the `.env` file and fill in the required credentials (API keys, tokens, passwords for Gmail, Slack, MoneyForward, etc.). Refer to the comments in `.env.development` for details.
    *   **Important:** Ensure the `.env` file is listed in your `.gitignore` (it is by default).

4.  **Configure Cloudflare D1:**
    *   Edit `wrangler.toml`.
    *   Update `database_id` in the `[[d1_databases]]` section with your actual Cloudflare D1 database ID for deployment. The `preview_database_id` is used by `wrangler dev` if you choose not to use local emulation via Miniflare.
    *   The database schema is defined in `schema.sql`. You'll need to apply this to your Cloudflare D1 database, either via the Cloudflare dashboard or using `wrangler d1 execute <YOUR_DB_NAME> --file=./schema.sql`. For local development, this is typically handled automatically by Miniflare based on `wrangler.toml`.

## Local Development

1.  **Run the Local D1 Emulator & Worker:**
    *   The project uses Miniflare via the Wrangler CLI to emulate the Cloudflare environment locally, including the D1 database.
    *   Start the local development server:
        ```bash
        npx wrangler dev
        ```
    *   This command reads `wrangler.toml`, sets up a local D1 database (persisted in `.wrangler/`), applies the `schema.sql` if the DB is new, and starts a local server mimicking the Cloudflare environment. Your Mastra application (defined in `src/`) will run within this environment.

2.  **Run Playwright MCP (Separately):**
    *   For local testing of Playwright automation, you need to run the Playwright MCP service in a separate terminal:
        ```bash
        npx @playwright/mcp@latest
        ```
    *   Ensure your Mastra configuration points to the local MCP instance (usually `ws://localhost:31415` by default).

3.  **Access Mastra Dev UI (if configured):**
    *   If you have set up the Mastra Dev UI (`@mastra/dev-ui`), access it via the specified port (often `http://localhost:4111`) to interact with your agents and workflows.

## Testing

-   **Run all tests:**
    ```bash
    npm test
    ```
-   **Unit Tests (Jest):** Located in `tests/utils/` and `tests/nodes/`. They test individual functions and classes in isolation, mocking external dependencies where appropriate. Uses Jest.
-   **Integration Tests (Jest):** Located in `tests/integration/`. These tests verify the interaction between components, particularly focusing on the `D1Client` interacting with the *local* D1 database provided by Miniflare during the test run. Uses Jest.
-   **End-to-End Tests (Playwright):** Located in `tests/e2e/`. These tests simulate the entire workflow, potentially involving fetching real emails (from a test account), interacting with the D1 database, and performing actions in a real browser via Playwright MCP. Uses Playwright's test runner. *(Setup for E2E tests might require specific test accounts and data)*.

See `development.mdc` for more detailed testing strategies and guidelines.

## Deployment & Execution

-   **Cloudflare Workers (Recommended):** Deploy the application as a Cloudflare Worker using `npx wrangler deploy`. The workflow can then be triggered via HTTP requests or Cron Triggers configured in `wrangler.toml`.
-   **GitHub Actions:** Alternatively, use GitHub Actions workflows (defined in `.github/workflows/`) for scheduled execution. Ensure all necessary secrets are configured in the repository settings.

## Project Structure Overview

```
.
├── .github/          # GitHub Actions workflows
├── .cursor/          # Cursor IDE specific settings (rules, etc.)
├── .wrangler/        # Local development state (Miniflare D1 DB, etc. - ignored by git)
├── docs/             # Project documentation (design docs, etc.)
├── src/              # Source code
│   ├── lib/          # Core libraries (e.g., d1Client.ts)
│   ├── mastra/       # Mastra specific components
│   │   ├── agents/   # Mastra agent definitions
│   │   ├── tools/    # Custom tools for agents (Gmail, Parser, Playwright)
│   │   └── workflows/# Mastra workflow definitions (YAML or TS)
│   └── index.ts      # Main application entry point / Mastra config
├── tests/            # Automated tests
│   ├── e2e/          # End-to-end tests (Playwright)
│   ├── integration/  # Integration tests (Jest, interacts with local D1)
│   └── utils/        # Unit tests for utilities (Jest)
├── .env.development  # Example environment variables
├── .gitignore        # Specifies intentionally untracked files
├── development.mdc   # Detailed development workflow & guidelines (Cursor rule)
├── jest.config.cjs   # Jest configuration
├── LICENSE           # Project license (MIT)
├── package.json      # Project metadata and dependencies
├── README.md         # This file
├── schema.sql        # Cloudflare D1 database schema
├── tsconfig.json     # TypeScript configuration
└── wrangler.toml     # Cloudflare Wrangler configuration (Worker, D1 bindings)
```

## Development Guidelines

Please refer to `development.mdc` for detailed guidelines on:

-   Development environment setup
-   TypeScript usage
-   Error handling
-   Testing strategy
-   Documentation standards (TSDoc)
-   Code review process

Refer to `basic.mdc` for general rules like branching, commit messages (Conventional Commits), and PR procedures.

## License

MIT 
