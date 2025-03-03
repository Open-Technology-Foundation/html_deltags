# HTML Deltags Development Guide

## Environment & Commands
- Setup: `pip install -r requirements.txt`
- Run script: `python html_deltags.py [options] [input_file]`
- Run with specific parser: `python html_deltags.py -p html5lib [options] [input_file]`
- Test: `python -m unittest discover`

## Code Style Guidelines
- Python version: >= 3.10
- Imports: Group standard library imports first, then third-party
- Indentation: 2 spaces
- Docstrings: Use triple double-quotes with Google-style format
- Type hints: Use for function parameters and return values
- Variable naming: snake_case for variables, PascalCase for classes
- Error handling: Use specific exceptions and meaningful error messages
- CLI arguments: Parse with sys.argv with clear error handling for missing args
- File handling: Always use context managers (with statements) and UTF-8 encoding
- String formatting: Use f-strings for better readability

## Project Structure
- html_deltags.py: Main module with HTML processing functionality
- extract_a.py: Utility for extracting links from HTML documents
- Requirements: beautifulsoup4, html5lib