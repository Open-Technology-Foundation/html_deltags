#!/usr/bin/env python3
"""html_extract - html tag contents extractor

The html_extract script processes an HTML file (or stdin) by extracting the contents of specified tags and outputs the results to a file or stdout.

Usage:
  html_extract [options] selector [input_file]

Arguments:
  selector
      CSS-like selector for tags to extract (e.g. 'p', 'section.p', 'head.title').
      For nested selectors, use dot notation (e.g. 'div.p' for all paragraphs inside divs).
  input_file
      Path to HTML file to process.
      Reads from stdin if not provided.

Options:
  -O|--output filename
      Output file for extracted content.
      Defaults to stdout.
  -p|--parser html5lib|lxml|html.parser
      BS4 html parser to use.
      Default: html5lib
  -i|--include-tags
      Include the opening and closing tags in the output.
      Default: only extract text content.
  -r|--raw
      Extract raw HTML content without processing.
      Preserves original formatting, whitespace, and indentation.
      Includes the enclosing tags. Overrides --include-tags.
  -n|--no-newlines
      Output items on a single line separated by spaces.
      Default: each item is on its own line.
  -a|--attributes
      Include specified attributes in output (comma-separated list) or
      filter tags by attributes (show only tags with these attributes).
      Example: -a class,id
  -h|--help
      Display this help message and exit.

Parsers:
  Each of the parsers has its strengths and weaknesses.

  Speed: lxml is the fastest, followed by html.parser, then html5lib.

  Error Tolerance: html5lib and lxml are more forgiving of broken HTML compared to html.parser.

  Dependencies: html.parser has the advantage of not requiring any external dependencies.

  Standards Conformance: html5lib is best for parsing HTML in a way consistent with modern browsers.

Examples:
  html_extract p my.html
  
  html_extract -i section.p < my.html > extracted.txt
  
  html_extract div.h2 my.html -O headers.txt
  
  html_extract head.title my.html
  
  html_extract -a href a my.html

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
from typing import List, Tuple, Union, Optional, TextIO, Dict
from bs4 import BeautifulSoup, Tag, NavigableString

# Define supported parsers
SUPPORTED_PARSERS = ["html5lib", "lxml", "html.parser"]

class HTMLProcessingError(Exception):
    """Custom exception for HTML processing errors."""
    pass

def parse_nested_selector(selector: str) -> List[str]:
    """
    Parse a nested selector like 'div.p.span' into its component parts.
    
    Args:
        selector: A CSS-like selector string using dot notation for nesting
        
    Returns:
        List of tag names in hierarchical order
    """
    return selector.strip().split('.')

def extract_tag_contents(
    input_source: Union[str, TextIO],
    output: Union[str, TextIO],
    selector: str,
    parser: str = 'html5lib',
    include_tags: bool = False,
    compact_output: bool = False,
    raw_mode: bool = False,
    attributes: Optional[List[str]] = None
) -> str:
    """
    Extract contents from specified HTML tags.
    
    Args:
        input_source: The source of the HTML content. Can be a file path or file-like object.
        output: The destination for the extracted content. Can be a file path or file-like object.
        selector: CSS-like selector for tags to extract (e.g. 'p', 'section.p', 'head.title').
        parser: The BeautifulSoup parser to use ('html5lib', 'lxml', 'html.parser').
        include_tags: Whether to include the opening and closing tags in the output.
        compact_output: Whether to output items on a single line with space separators.
        raw_mode: Whether to extract the raw HTML content without processing.
        attributes: List of attribute names to include in the output.
        
    Returns:
        str: The extracted content.
        
    Raises:
        HTMLProcessingError: If there's an error processing the HTML content.
        ValueError: If an invalid parser is specified.
        IOError: If there's an error reading from or writing to files.
    """
    # Validate parser
    if parser not in SUPPORTED_PARSERS:
        raise ValueError(f"Invalid parser: {parser}. Supported parsers: {', '.join(SUPPORTED_PARSERS)}")
    
    # Initialize attributes if not provided
    if attributes is None:
        attributes = []
    
    # Process the HTML content
    try:
        # Read input for both raw and regular mode
        source_html = ""
        if isinstance(input_source, str):
            try:
                with open(input_source, 'r', encoding='utf-8') as file:
                    source_html = file.read()
                    # For regular processing mode, create BeautifulSoup object
                    if not raw_mode:
                        soup = BeautifulSoup(source_html, parser)
            except Exception as e:
                raise IOError(f"Error reading input file: {e}")
        else:
            # Handle file-like objects
            if hasattr(input_source, 'read'):
                source_html = input_source.read()
                # If it's stdin or another file-like object, reset to beginning if possible
                if hasattr(input_source, 'seek') and hasattr(input_source, 'tell'):
                    current_pos = input_source.tell()
                    input_source.seek(0)
                    source_html = input_source.read()
                    input_source.seek(current_pos)  # Restore position
                
                if not raw_mode:
                    soup = BeautifulSoup(source_html, parser)
            else:
                # If it's already a string or other content, use directly
                source_html = str(input_source)
                if not raw_mode:
                    soup = BeautifulSoup(source_html, parser)
        
        # Parse the selector
        tag_hierarchy = parse_nested_selector(selector)
        
        extracted_content = []
        
        if raw_mode:
            # For raw mode, use regex to extract the exact original content
            main_tag = tag_hierarchy[0]
            pattern = rf'<{main_tag}(?:\s+[^>]*)?>(.*?)</{main_tag}>'
            
            # For nested selectors in raw mode, we focus on the first level tag only
            # This is a limitation, but raw extraction with nested selectors is complex
            
            # Find all instances including the tags
            matches = re.finditer(pattern, source_html, re.DOTALL)
            for match in matches:
                full_match = match.group(0)  # The entire match including tags
                if full_match:
                    extracted_content.append(full_match)
        else:
            # Process nested selectors in regular mode
            if len(tag_hierarchy) > 1:
                # Start with the first tag
                current_tags = soup.find_all(tag_hierarchy[0])
                
                # For each subsequent tag in the hierarchy, filter down
                for i in range(1, len(tag_hierarchy)):
                    # Find all nested tags within the current set
                    nested_tags = []
                    for tag in current_tags:
                        nested_tags.extend(tag.find_all(tag_hierarchy[i], recursive=True))
                    current_tags = nested_tags
            else:
                # Single tag selector
                current_tags = soup.find_all(tag_hierarchy[0])
            
            # Extract content from matched tags in regular mode
            for tag in current_tags:
                # Filter tags by attributes if specified
                if attributes:
                    # Special case for meta description tags
                    if 'name' in attributes and 'description' in attributes and tag.name == 'meta':
                        # Only include meta tags with name="description" or property="og:description" etc.
                        has_name_attr = tag.has_attr('name') or tag.has_attr('property')
                        is_description = False
                        
                        if has_name_attr:
                            name_val = tag.get('name') or tag.get('property') or ''
                            is_description = 'description' in name_val.lower()
                        
                        if not (has_name_attr and is_description):
                            continue
                    # For other cases, any of the specified attributes must be present
                    elif not any(tag.has_attr(attr) for attr in attributes):
                        continue
                
                if include_tags:
                    # Include the entire tag with its content
                    content = str(tag)
                else:
                    # Extract just the text content
                    # Use separator=' ' to ensure spaces between text nodes
                    content = tag.get_text(separator=' ', strip=True)
                
                # Add attributes if requested
                attr_content = ""
                if attributes:
                    for attr in attributes:
                        attr_value = tag.get(attr)
                        if attr_value:
                            if isinstance(attr_value, list):
                                attr_value = ' '.join(attr_value)
                            attr_content += f" [{attr}=\"{attr_value}\"]"
                    
                    if attr_content and not include_tags:
                        content = f"{content}{attr_content}"
                
                if content or include_tags:  # Include empty tags when using -i
                    extracted_content.append(content)
        
        # Join extracted content
        separator = ' ' if compact_output else '\n'
        result = separator.join(extracted_content)
        
        # Output the extracted content
        if isinstance(output, str):
            try:
                with open(output, 'w', encoding='utf-8') as file:
                    file.write(result)
            except Exception as e:
                raise IOError(f"Error writing to output file: {e}")
        else:
            output.write(result)
        
        return result
    
    except Exception as e:
        # Catch and re-raise exceptions with more context
        if isinstance(e, (ValueError, IOError, HTMLProcessingError)):
            raise
        else:
            raise HTMLProcessingError(f"Error processing HTML: {str(e)}")

def validate_arguments(parser: str, selector: str, input_file: Optional[str]) -> None:
    """
    Validate command-line arguments.
    
    Args:
        parser: The parser name to validate.
        selector: The CSS selector to validate.
        input_file: The input file path to validate (if provided).
        
    Raises:
        ValueError: If invalid arguments are provided.
    """
    # Validate parser
    if parser not in SUPPORTED_PARSERS:
        raise ValueError(f"Invalid parser: {parser}. Supported parsers: {', '.join(SUPPORTED_PARSERS)}")
    
    # Validate selector (basic validation)
    if not selector or not all(part.strip() for part in selector.split('.')):
        raise ValueError(f"Invalid selector: {selector}. Use tag names separated by dots for nested selectors.")
    
    # Validate input file (if specified)
    if input_file and not os.path.isfile(input_file):
        raise ValueError(f"Input file does not exist: {input_file}")

def parse_arguments() -> Tuple[
    str, Optional[str], Union[str, TextIO], str, bool, bool, bool, List[str]
]:
    """
    Parse command-line arguments.
    
    Returns:
        Tuple containing selector, input source, output destination, parser name,
        include_tags flag, compact_output flag, raw_mode flag, and attributes list.
    """
    # Initialize default values
    selector = None
    input_source = None
    output_file = sys.stdout
    parser = 'html5lib'
    include_tags = False
    compact_output = False
    raw_mode = False
    attributes = []
    
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
            
        # Include tags
        elif arg in ('-i', '--include-tags'):
            include_tags = True
            
        # Raw mode
        elif arg in ('-r', '--raw'):
            raw_mode = True
            
        # Compact output (no newlines)
        elif arg in ('-n', '--no-newlines'):
            compact_output = True
            
        # Attributes to include
        elif arg in ('-a', '--attributes'):
            if index + 1 >= len(sys.argv):
                print(f"{os.path.basename(__file__)}: error: '{arg}' option requires an argument", 
                      file=sys.stderr)
                sys.exit(1)
            attributes = sys.argv[index + 1].split(',')
            index += 1
            
        # Selector (first positional argument)
        elif selector is None:
            selector = arg
            
        # Input source (second positional argument)
        elif input_source is None:
            input_source = arg
            
        # Unexpected argument
        else:
            print(f"{os.path.basename(__file__)}: error: unexpected argument '{arg}'", 
                  file=sys.stderr)
            sys.exit(1)
            
        index += 1
    
    # Selector is required
    if selector is None:
        print(f"{os.path.basename(__file__)}: error: selector argument is required", 
              file=sys.stderr)
        sys.exit(1)
    
    # Default to stdin if no input file provided
    if input_source is None:
        input_source = sys.stdin
        
    return selector, input_source, output_file, parser, include_tags, compact_output, raw_mode, attributes

def main() -> int:
    """
    Main entry point for the script.
    
    Returns:
        int: Exit code (0 for success, non-zero for errors).
    """
    try:
        # Parse arguments
        selector, input_source, output_file, parser, include_tags, compact_output, raw_mode, attributes = parse_arguments()
        
        # Validate arguments
        if isinstance(input_source, str):
            validate_arguments(parser, selector, input_source)
        else:
            validate_arguments(parser, selector, None)
        
        # Process HTML
        extract_tag_contents(input_source, output_file, selector, parser, include_tags, compact_output, raw_mode, attributes)
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