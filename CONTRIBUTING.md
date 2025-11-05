# Contributing to Spoticron

Thank you for your interest in contributing to Spoticron! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/spoticron.git
   cd spoticron
   ```
3. **Set up development environment**:
   ```bash
   make install-dev
   make setup-pre-commit
   ```

For detailed development setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md). 5. **Set up your Spotify API credentials** (see README.md)

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to all public functions and classes
- Keep line length under 80 characters

### Testing

- Write tests for new features
- Run existing tests before submitting: `python -m pytest tests/`
- Ensure all tests pass

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add detailed description if needed

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Steps to reproduce the issue
- Expected vs actual behavior
- Your operating system and Python version
- Relevant error messages or logs

### Feature Requests

- Describe the feature and why it would be useful
- Provide examples of how it would work
- Consider if it fits with the project's goals

### Code Contributions

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes**
3. **Test your changes**
4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request** on GitHub

### Documentation

- Fix typos and improve clarity
- Add examples and use cases
- Update README.md for new features

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation if needed
3. Add or update tests for your changes
4. Ensure all tests pass
5. Update CHANGELOG.md if applicable
6. Your PR will be reviewed by maintainers

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help create a welcoming environment for all contributors

## Questions?

If you have questions about contributing, feel free to:

- Open an issue on GitHub
- Start a discussion in the project's discussions section

Thank you for contributing to Spoticron! 🎵
