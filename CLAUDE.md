# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Run script: `python payment-checker.py --config config.yaml`
- Install dependencies: `pip install -r requirements.txt` (create this if needed)

## Code Style Guidelines
- **Imports**: Group standard library imports first, then third-party packages, then local modules
- **Formatting**: Use 4 spaces for indentation
- **Error Handling**: Use try/except blocks with specific exception handling
- **Naming**: Use snake_case for functions and variables, CamelCase for classes
- **Documentation**: Include docstrings for functions and detailed comments for complex logic
- **Function Design**: Keep functions focused on a single responsibility
- **Browser Automation**: Take screenshots at key steps for debugging
- **Config**: Use YAML for configuration, never hardcode credentials

When making changes, ensure backward compatibility with existing provider modules and maintain the same pattern for any new provider implementations.