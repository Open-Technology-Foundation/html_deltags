# HTML Deltags Development Guide

## Environment & Commands
- Setup: `pip install -r requirements.txt`
- Run script: `python html_deltags.py [options] [input_file]`
- Run with specific parser: `python html_deltags.py -p html5lib [options] [input_file]`
- Extract links: `python extract_a.py < input.html`
- Lint: `flake8 *.py` or `pylint *.py`
- Type check: `mypy *.py`

## Code Style Guidelines
- Python version: >= 3.10
- Imports: Group standard library imports first, then third-party imports
- Indentation: 2 spaces for extract_a.py, 4 spaces for html_deltags.py
- Docstrings: Triple double-quotes with Google-style format
- Type hints: Required for function parameters and return values
- Variable naming: snake_case for variables/functions, PascalCase for classes
- Error handling: Use specific exceptions (HTMLProcessingError, ValueError, IOError)
- CLI arguments: Parse with sys.argv, handle missing arguments with clear errors
- File handling: Always use context managers (with statements) and UTF-8 encoding
- String formatting: Use f-strings for better readability

## Project Structure
- html_deltags.py: Main module with HTML processing functionality
- extract_a.py: Utility for extracting links from HTML documents
- Requirements: beautifulsoup4 (>=4.10.0), html5lib (>=1.1), typing_extensions (>=4.0.0)