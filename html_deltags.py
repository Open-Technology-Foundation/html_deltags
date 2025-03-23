#!/usr/bin/env python3
"""html_deltags - html tag-remover/reformatter

The html_deltags script processes an HTML file (or stdin) by removing specified tags and comments, then outputs detagged/minified HTML to a file or stdout.

Usage:
  html_deltags [options] [input_file]

Arguments:
  input_file
      Path to HTML file to be detagged/minified.
      Reads from stdin if not provided.

Options:
  -O|--output filename
      Output file for detagged HTML.
      Defaults to stdout.
  -d|--delete tag[,tag,tag]
      HTML tags to remove, as a comma-separated list.
      Multiple -d options allowed.
      Example: ... -d script,link,meta ...
  -k|--kw-delete 'tag keyword'
      Remove tags containing specific keywords in class attribute.
      Specify tag, space, then the exact class or pattern to match.
      Multiple -k options allowed.
      Example: ... -k 'div elementor-widget-container' ...
  -a|--attr-delete 'tag attr value'
      Remove tags with specific attribute values.
      Specify tag, attribute name, value pattern.
      Multiple -a options allowed.
      Example: ... -a 'div id sidebar' ...
  -p|--parser html5lib|lxml|html.parser
      BS4 html parser to use.
      Default: html5lib
  -m|--minify
      Enable full minification (removes whitespace).
      Default: pretty-print with minimal formatting.
  -h|--help
      Display this help message and exit.

Parsers:
  Each of the parsers has its strengths and weaknesses.

  Speed: lxml is the fastest, followed by html.parser, then html5lib.

  Error Tolerance: html5lib and lxml are more forgiving of broken HTML compared to html.parser.

  Dependencies: html.parser has the advantage of not requiring any external dependencies.

  Standards Conformance: html5lib is best for parsing HTML in a way consistent with modern browsers.

Examples:
  html_deltags my.html -d head,comments,nav

  html_deltags -d head,comments,nav < my.html > mynew.html

  html_deltags my.html -d head,comments,nav -d svg,path -O mynew.html

  html_deltags my.html -d head,nav -k 'div sometext' -a 'div id sidebar'

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
from typing import List, Tuple, Union, Optional, TextIO
from bs4 import BeautifulSoup, Comment, Tag

# Define supported parsers
SUPPORTED_PARSERS = ["html5lib", "lxml", "html.parser"]

class HTMLProcessingError(Exception):
    """Custom exception for HTML processing errors."""
    pass

def html_deltags(
    input_source: Union[str, TextIO], 
    output: Union[str, TextIO], 
    deltags: List[str], 
    deltagkws: List[Tuple[str, str]], 
    delattrvals: Optional[List[Tuple[str, str, str]]] = None,
    parser: str = 'html5lib',
    minify: bool = False
) -> str:
    """
    Detags/minimizes an HTML document by removing specified tags and comments.

    Args:
        input_source: The source of the HTML content. Can be a file path or file-like object.
        output: The destination for the detagged HTML content. Can be a file path or file-like object.
        deltags: List of tag names to remove from the HTML content.
        deltagkws: List of (tag, keyword) tuples to remove from the HTML content.
        delattrvals: Optional list of (tag, attribute, value) tuples for targeted removal.
        parser: The BeautifulSoup parser to use ('html5lib', 'lxml', 'html.parser').
        minify: Whether to fully minify output (True) or use pretty print (False).

    Returns:
        str: The processed HTML content.

    Raises:
        HTMLProcessingError: If there's an error processing the HTML content.
        ValueError: If an invalid parser is specified.
        IOError: If there's an error reading from or writing to files.
    """
    # Validate parser
    if parser not in SUPPORTED_PARSERS:
        raise ValueError(f"Invalid parser: {parser}. Supported parsers: {', '.join(SUPPORTED_PARSERS)}")

    # Initialize delattrvals if not provided
    if delattrvals is None:
        delattrvals = []
    
    # Process the HTML content
    try:
        # Read input
        if isinstance(input_source, str):
            try:
                with open(input_source, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, parser)
            except Exception as e:
                raise IOError(f"Error reading input file: {e}")
        else:
            soup = BeautifulSoup(input_source, parser)

        # Remove all instances of specified tags and comments
        for tag_name in deltags:
            try:
                if tag_name.lower() in ('comments', '!--'):
                    # Find and remove all comment tags
                    try:
                        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
                        for comment in comments:
                            comment.extract()
                    except Exception as e:
                        print(f"Warning: Error removing comments: {str(e)}", file=sys.stderr)
                        continue
                else:
                    # Find and remove all instances of the specified tag
                    try:
                        for tag in soup.find_all(tag_name):
                            try:
                                tag.decompose()
                            except (AttributeError, TypeError) as e:
                                # Skip this tag if any error occurs processing it
                                continue
                    except Exception as e:
                        print(f"Warning: Error removing tag '{tag_name}': {str(e)}", file=sys.stderr)
                        continue
            except Exception as e:
                print(f"Warning: Error processing tag type '{tag_name}': {str(e)}", file=sys.stderr)
                continue

        # Remove all instances of a specific tag that contains a keyword in class attribute
        for tag_name, keyword in deltagkws:
            try:
                for tag in soup.find_all(tag_name):
                    try:
                        # Get class value, handling both string and list representations
                        class_attr = tag.get('class')
                        if class_attr is not None:  # Check specifically for None
                            # Check for exact class match
                            if isinstance(class_attr, list):
                                # If it's a list, check if the keyword matches any class name exactly
                                if keyword in class_attr:
                                    tag.decompose()
                            else:
                                # If it's a string, split by whitespace and check for exact match
                                class_str = str(class_attr)  # Ensure it's a string
                                class_list = class_str.split()
                                if keyword in class_list:
                                    tag.decompose()
                    except (AttributeError, TypeError) as e:
                        # Skip this tag if any error occurs processing it
                        continue
            except Exception as e:
                # Log error and continue with next keyword
                print(f"Warning: Error processing tag '{tag_name}' with keyword '{keyword}': {str(e)}", file=sys.stderr)

        # Remove all instances of a tag with specific attribute values
        for tag_name, attr_name, attr_value in delattrvals:
            try:
                for tag in soup.find_all(tag_name):
                    try:
                        attr_val = tag.get(attr_name)
                        if attr_val is not None:  # Check specifically for None
                            # Handle both string and list attribute values
                            if isinstance(attr_val, list):
                                attr_str = ' '.join(attr_val)
                            else:
                                attr_str = str(attr_val)  # Ensure it's a string
                                
                            # Remove tag if attribute value contains the specified value
                            if attr_value in attr_str:
                                tag.decompose()
                    except (AttributeError, TypeError) as e:
                        # Skip this tag if any error occurs processing it
                        continue
            except Exception as e:
                # Log error and continue with next attribute search
                print(f"Warning: Error processing tag '{tag_name}' with attribute '{attr_name}': {str(e)}", file=sys.stderr)

        # Format the HTML
        if minify:
            # Full minification
            processed_html = "".join(str(soup).split())
        else:
            # Pretty print with minimal formatting
            processed_html = soup.prettify(formatter="minimal")

        # Output the processed HTML
        if isinstance(output, str):
            try:
                with open(output, 'w', encoding='utf-8') as file:
                    file.write(processed_html)
            except Exception as e:
                raise IOError(f"Error writing to output file: {e}")
        else:
            output.write(processed_html)

        return processed_html

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
    Optional[str], Union[str, TextIO], List[str], List[Tuple[str, str]], 
    List[Tuple[str, str, str]], str, bool
]:
    """
    Parse command-line arguments.
    
    Returns:
        Tuple containing input source, output destination, tags to delete,
        tag-keyword pairs to delete, tag-attribute-value triples to delete,
        parser name, and minify flag.
    """
    # Initialize default values
    input_source = None
    output_file = sys.stdout
    deltags = []
    deltagkws = []
    delattrvals = []
    parser = 'html5lib'
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
            
        # Tags to delete
        elif arg in ('-d', '--delete'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            deltags.extend(sys.argv[index + 1].split(','))
            index += 1
            
        # Tag+keyword delete
        elif arg in ('-k', '--kw-delete'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            parts = sys.argv[index + 1].split(' ', 1)
            if len(parts) < 2:
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires 'tag keyword' format", 
                      file=sys.stderr)
                sys.exit(1)
            deltagkws.append((parts[0], parts[1]))
            index += 1
            
        # Tag+attribute+value delete
        elif arg in ('-a', '--attr-delete'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            parts = sys.argv[index + 1].split(' ', 2)
            if len(parts) < 3:
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires 'tag attr value' format", 
                      file=sys.stderr)
                sys.exit(1)
            delattrvals.append((parts[0], parts[1], parts[2]))
            index += 1
            
        # Minify option
        elif arg in ('-m', '--minify'):
            minify = True
            
        # Input source
        elif input_source is None:
            input_source = arg
            # Input file validation moved to validate_arguments()
            
        # Unexpected argument
        else:
            print(f"{os.path.basename(__file__)}: error: unexpected argument '{arg}'", 
                  file=sys.stderr)
            sys.exit(1)
            
        index += 1
    
    # Default to stdin if no input file provided
    if input_source is None:
        input_source = sys.stdin
        
    return input_source, output_file, deltags, deltagkws, delattrvals, parser, minify

def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Parse arguments
        input_source, output_file, deltags, deltagkws, delattrvals, parser, minify = parse_arguments()
        
        # Validate arguments
        if isinstance(input_source, str):
            validate_arguments(parser, input_source)
        else:
            validate_arguments(parser, None)
        
        # Process HTML
        html_deltags(input_source, output_file, deltags, deltagkws, delattrvals, parser, minify)
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