# Contributing to Discord Auto Counter Bot

Thank you for your interest in contributing to the Discord Auto Counter Bot! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Screenshots if relevant
6. Your environment (OS, Python version, etc.)

**IMPORTANT**: When sharing configuration files or logs, use the `scripts/clean_config.py` utility to remove sensitive information.

### Suggesting Features

Feature suggestions are welcome! When suggesting a feature:

1. Explain the problem you're trying to solve
2. Describe your solution
3. Explain alternatives you've considered
4. Add any relevant mockups or examples

### Pull Requests

1. Fork the repository
2. Create a branch from `main`: `git checkout -b feature/my-new-feature`
3. Make your changes
4. Update tests if applicable
5. Update documentation as needed
6. Submit a pull request against the `main` branch

### Coding Standards

Follow the project's coding standards as documented in [docs/CODING_STANDARDS.md](docs/CODING_STANDARDS.md).

## Development Setup

1. Clone the repository: `git clone https://github.com/yourusername/discord-countingbot.git`
2. Install requirements: `pip install -r requirements.txt`
3. Create a configuration file: `python setup.py`
4. Run the bot: `python auto_counter.py`

## Pull Request Process

1. Ensure all code follows the project's coding standards
2. Update documentation as needed
3. Make sure tests pass (if applicable)
4. The PR will be reviewed by project maintainers
5. Once approved, the PR will be merged

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License as found in the [LICENSE](LICENSE) file.

## Questions?

If you have any questions about contributing, please open an issue or contact the project maintainers. 