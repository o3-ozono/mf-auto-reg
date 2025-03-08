# mf-auto-reg

This repository contains a Python script that automatically extracts transaction information from ANA Pay email notifications in Gmail and registers it in MoneyForward.

## Description

This script automates the process of extracting transaction details (date, amount, store) from ANA Pay email notifications received in Gmail and registering them in MoneyForward.

## Prerequisites

- Python 3.11+
- uv

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/o3-ozono/mf-auto-reg.git
    ```

2.  Create a virtual environment:

    ```bash
    uv venv
    ```

3.  Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

4.  Install the dependencies:

    ```bash
    uv sync
    ```

## Usage

1.  Create a `credentials.json` file. This file can be downloaded after creating an OAuth 2.0 client ID in the Google Cloud Platform.

2.  Run the script:

    ```bash
    uv run gmail_to_moneyforward.py
    ```

## License

MIT
