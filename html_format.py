#!/usr/bin/env python3
"""html_format - html formatting/indentation tool

The html_format script processes an HTML file (or stdin) and outputs properly formatted and indented HTML.

Usage:
  html_format [options] [input_file]

Arguments:
  input_file
      Path to HTML file to be formatted.
      Reads from stdin if not provided.

Options:
  -O|--output filename
      Output file for formatted HTML.
      Defaults to stdout.
  -p|--parser html5lib|lxml|html.parser
      BS4 html parser to use.
      Default: html5lib
  -i|--indent SPACES
      Number of spaces for indentation.
      Default: 2
  -m|--minify
      Minify HTML instead of prettifying it.
      Removes all unnecessary whitespace.
  -h|--help
      Display this help message and exit.

Parsers:
  Each of the parsers has its strengths and weaknesses.

  Speed: lxml is the fastest, followed by html.parser, then html5lib.

  Error Tolerance: html5lib and lxml are more forgiving of broken HTML compared to html.parser.

  Dependencies: html.parser has the advantage of not requiring any external dependencies.

  Standards Conformance: html5lib is best for parsing HTML in a way consistent with modern browsers.

Examples:
  html_format my.html
  
  html_format -i 4 < my.html > formatted.html
  
  html_format my.html -O formatted.html
  
  html_format -m my.html

Requires:
  Python >= 3.10
  pip:beautifulsoup4 >= 4.10.0
  pip:html5lib (recommended parser)
  pip:typing_extensions (for beautifulsoup4)
  Bash >= 5.0

Repository:
  https://github.com/Open-Technology-Foundation/html_deltags
"""

import os
import sys
import re
from typing import List, Tuple, Union, Optional, TextIO
from bs4 import BeautifulSoup, Tag

# Define supported parsers
SUPPORTED_PARSERS = ["html5lib", "lxml", "html.parser"]

class HTMLProcessingError(Exception):
    """Custom exception for HTML processing errors."""
    pass

def format_html(
    input_source: Union[str, TextIO],
    output: Union[str, TextIO],
    parser: str = 'html5lib',
    indent: int = 2,
    minify: bool = False
) -> str:
    """
    Format HTML with proper indentation.
    
    Args:
        input_source: The source of the HTML content. Can be a file path or file-like object.
        output: The destination for the formatted HTML. Can be a file path or file-like object.
        parser: The BeautifulSoup parser to use ('html5lib', 'lxml', 'html.parser').
        indent: Number of spaces for indentation (ignored if minify=True).
        minify: Whether to minify the HTML (remove all whitespace).
        
    Returns:
        str: The formatted HTML content.
        
    Raises:
        HTMLProcessingError: If there's an error processing the HTML content.
        ValueError: If an invalid parser is specified.
        IOError: If there's an error reading from or writing to files.
    """
    # Validate parser
    if parser not in SUPPORTED_PARSERS:
        raise ValueError(f"Invalid parser: {parser}. Supported parsers: {', '.join(SUPPORTED_PARSERS)}")
    
    # Process the HTML content
    try:
        # Read input
        if isinstance(input_source, str):
            try:
                with open(input_source, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                    # Fix potential malformed doctype before parsing
                    if html_content.strip().startswith("<\\!DOCTYPE"):
                        html_content = html_content.replace("<\\!DOCTYPE", "<!DOCTYPE")
                    soup = BeautifulSoup(html_content, parser)
            except Exception as e:
                raise IOError(f"Error reading input file: {e}")
        else:
            if hasattr(input_source, 'read'):
                html_content = input_source.read()
                # Fix potential malformed doctype before parsing
                if isinstance(html_content, str) and html_content.strip().startswith("<\\!DOCTYPE"):
                    html_content = html_content.replace("<\\!DOCTYPE", "<!DOCTYPE")
                soup = BeautifulSoup(html_content, parser)
            else:
                html_content = str(input_source)
                # Fix potential malformed doctype before parsing
                if html_content.strip().startswith("<\\!DOCTYPE"):
                    html_content = html_content.replace("<\\!DOCTYPE", "<!DOCTYPE")
                soup = BeautifulSoup(html_content, parser)
        
        # Format the HTML
        if minify:
            # Minify the HTML by removing all whitespace
            formatted_html = str(soup).replace('\n', '')
            formatted_html = re.sub(r'>\s+<', '><', formatted_html)
            formatted_html = re.sub(r'\s{2,}', ' ', formatted_html)
            formatted_html = re.sub(r'<!--.*?-->', '', formatted_html)
        else:
            # Prettify with specified indentation
            indent_str = ' ' * indent
            
            # First prettify the HTML with default indentation
            formatted_html = soup.prettify(formatter="minimal")
            
            # Then adjust the indentation level if needed (if not default 2 spaces)
            if indent != 2:
                # Replace each level of indentation with our custom indent
                lines = formatted_html.split('\n')
                for i in range(len(lines)):
                    # Count leading spaces to determine indentation level
                    line = lines[i]
                    leading_spaces = len(line) - len(line.lstrip(' '))
                    if leading_spaces > 0:
                        # Calculate the indentation level
                        level = leading_spaces // 2
                        # Replace with our custom indentation
                        lines[i] = (indent_str * level) + line.lstrip(' ')
                
                formatted_html = '\n'.join(lines)
            
            # Clean up the formatted HTML to ensure consistent indentation
            # This is particularly helpful for self-closing tags while preserving proper tag nesting
            # We no longer collapse closing tags as that causes improper formatting
            # The original problematic line was: formatted_html = re.sub(r'>\s+</', '></', formatted_html)
        
        # Output the formatted HTML
        if isinstance(output, str):
            try:
                with open(output, 'w', encoding='utf-8') as file:
                    file.write(formatted_html)
            except Exception as e:
                raise IOError(f"Error writing to output file: {e}")
        else:
            output.write(formatted_html)
        
        return formatted_html
    
    except Exception as e:
        # Catch and re-raise exceptions with more context
        if isinstance(e, (ValueError, IOError, HTMLProcessingError)):
            raise
        else:
            raise HTMLProcessingError(f"Error processing HTML: {str(e)}")

def validate_arguments(parser: str, input_file: Optional[str]) -> None:
    """
    Validate command-line arguments.
    
    Args:
        parser: The parser name to validate.
        input_file: The input file path to validate (if provided).
        
    Raises:
        ValueError: If invalid arguments are provided.
    """
    # Validate parser
    if parser not in SUPPORTED_PARSERS:
        raise ValueError(f"Invalid parser: {parser}. Supported parsers: {', '.join(SUPPORTED_PARSERS)}")
    
    # Validate input file (if specified)
    if input_file and not os.path.isfile(input_file):
        raise ValueError(f"Input file does not exist: {input_file}")

def parse_arguments() -> Tuple[
    Optional[str], Union[str, TextIO], str, int, bool
]:
    """
    Parse command-line arguments.
    
    Returns:
        Tuple containing input source, output destination, parser name,
        indent size, and minify flag.
    """
    # Initialize default values
    input_source = None
    output_file = sys.stdout
    parser = 'html5lib'
    indent = 2
    minify = False
    
    # Process command-line arguments
    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        
        # Help
        if arg in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
            
        # Output file
        elif arg in ('-O', '--output'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            output_file = sys.argv[index + 1]
            index += 1
            
        # Parser
        elif arg in ('-p', '--parser'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            parser = sys.argv[index + 1]
            index += 1
            
        # Indent size
        elif arg in ('-i', '--indent'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            try:
                indent = int(sys.argv[index + 1])
                if indent < 0:
                    raise ValueError("Indent must be a non-negative integer.")
            except ValueError as e:
                print(f"{os.path.basename(__file__)}: error: {str(e)}", file=sys.stderr)
                sys.exit(1)
            index += 1
            
        # Minify
        elif arg in ('-m', '--minify'):
            minify = True
            
        # Input source (positional argument)
        elif input_source is None:
            input_source = arg
            
        # Unexpected argument
        else:
            print(f"{os.path.basename(__file__)}: error: unexpected argument '{arg}'", 
                  file=sys.stderr)
            sys.exit(1)
            
        index += 1
    
    # Default to stdin if no input file provided
    if input_source is None:
        input_source = sys.stdin
        
    return input_source, output_file, parser, indent, minify

def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Parse arguments
        input_source, output_file, parser, indent, minify = parse_arguments()
        
        # Validate arguments
        if isinstance(input_source, str):
            validate_arguments(parser, input_source)
        else:
            validate_arguments(parser, None)
        
        # Process HTML
        format_html(input_source, output_file, parser, indent, minify)
        return 0
        
    except ValueError as e:
        print(f"{os.path.basename(__file__)}: error: {str(e)}", file=sys.stderr)
        return 1
        
    except IOError as e:
        print(f"{os.path.basename(__file__)}: error: {str(e)}", file=sys.stderr)
        return 1
        
    except HTMLProcessingError as e:
        print(f"{os.path.basename(__file__)}: error: {str(e)}", file=sys.stderr)
        return 1
        
    except Exception as e:
        print(f"{os.path.basename(__file__)}: unexpected error: {str(e)}", file=sys.stderr)
        return 1

# If running as a shell script
if __name__ == '__main__':
    sys.exit(main())

#fin