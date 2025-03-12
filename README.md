# mf-auto-reg

This repository contains a Python script that automatically extracts transaction information from ANA Pay email notifications in Gmail and registers it in MoneyForward.

## Description

This script automates the process of extracting transaction details (date, amount, store) from ANA Pay email notifications received in Gmail and registering them in MoneyForward.

## Project Structure

The project follows the standard Python project structure:

```
mf-auto-reg/
├── src/                    # Source code directory
│   └── mf_auto_reg/        # Main package
│       ├── __init__.py     # Package initialization
│       ├── __main__.py     # Entry point
│       └── gmail_to_moneyforward.py  # Main module
├── tests/                  # Test directory
│   ├── __init__.py
│   ├── conftest.py         # Common test fixtures
│   ├── test_*.py           # Test modules
├── docs/                   # Documentation
├── examples/               # Example usage
├── pyproject.toml          # Project configuration
├── run_tests.py            # Test runner script
└── README.md               # This file
```

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

5.  Install the package in development mode:

    ```bash
    uv pip install -e .
    ```

## Usage

1.  Create a `credentials.json` file. This file can be downloaded after creating an OAuth 2.0 client ID in the Google Cloud Platform.
2.  Create a `.env` file and add your Gmail API credentials:

    ```
    CLIENT_ID=your_client_id
    CLIENT_SECRET=your_client_secret
    ```

3.  Run the script:

    ```bash
    uv run -m mf_auto_reg
    ```

    Or use the installed command:

    ```bash
    mf-auto-reg
    ```

## Testing

The tests are organized by functionality and located in the `tests` directory. To run the tests, use the following commands:

```bash
# Run all tests
uv run ./run_tests.py

# Or
uv run python -m unittest discover tests
```

### Test Structure

The tests are divided by functionality as follows:

- `tests/test_extract_information.py` - Tests for information extraction
- `tests/test_decode_message.py` - Tests for message decoding
- `tests/test_gmail_service.py` - Tests for Gmail API service
- `tests/test_email_operations.py` - Tests for email search and retrieval
- `tests/test_main.py` - Tests for the main function

To run only specific tests, use the following commands:

```bash
# Run a specific test file
uv run python -m unittest tests.test_extract_information

# Run a specific test class
uv run python -m unittest tests.test_extract_information.TestExtractInformation

# Run a specific test method
uv run python -m unittest tests.test_extract_information.TestExtractInformation.test_extract_information_valid_email
```

### Measuring Coverage

To measure code coverage, use the following commands:

```bash
# Run tests with coverage measurement
uv run coverage run -m unittest discover tests

# Display coverage report
uv run coverage report

# Display detailed coverage report (showing uncovered lines)
uv run coverage report -m
```

## License

MIT
