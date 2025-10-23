
# HTML Processing Tools

## `html_deltags` - html tag-remover/minimizer

Remove specific tags from a html file or stream and output detagged/minified HTML to file or stdout.

`html_deltags` is a Python module and Shell script designed to detag, normalize and 'minify' HTML documents. Removes specified HTML tags, including those containing certain keywords, and comments, streamlining further analysis of remaining HTML using clean input.

## `html_extract` - html tag contents extractor

Extract contents from specified tags in an HTML file or stream and output the results to a file or stdout.

`html_extract` is a complementary tool to `html_deltags` that allows you to extract content from specific HTML tags. It supports nested tag selection with a CSS-like selector syntax and can include additional tag attributes in the output.

## `html_format` - html formatter/indenter

Format HTML with proper indentation or minify it for compact output.

`html_format` helps clean up HTML files by applying consistent indentation, making them more readable and easier to maintain. It can also minify HTML by removing unnecessary whitespace for smaller file sizes.

## Features

### html_deltags
- Removes specified HTML tags and comments from an HTML document.
- Can target and delete tags based on contained keywords.
- Flexible usage as both a standalone script and an importable Python module.

### html_extract
- Extracts content from specified HTML tags using CSS-like selectors.
- Supports nested tag selection (e.g., 'section.p' for paragraphs inside sections).
- Can include opening and closing tags in the output.
- Option to include specific tag attributes in the output.
- Flexible output formatting with newline options.

### html_format
- Formats HTML with proper indentation to make it more readable.
- Customizable indentation size (spaces).
- Option to minify HTML by removing unnecessary whitespace.
- Uses BeautifulSoup for robust parsing of even malformed HTML.
- Support for different HTML parsers (html5lib, lxml, html.parser).

## Installation

    git clone https://github.com/Open-Technology-Foundation/html_deltags.git && sudo html_deltags/html_deltags.install
    
You can install all tools at once or individually as needed.

### html_deltags Installation

`html_deltags.install` will:
1. Copy html_deltags files to `/usr/local/share/html_deltags`
2. Create a Python virtual environment with all dependencies in the installation directory
3. Create a symlink at `/usr/local/bin/html_deltags`

Options:
- `--upgrade`: Download the latest version from the repository before installing

Example:
```
# Install normally
sudo ./html_deltags.install

# Install using the latest version from the repository
sudo ./html_deltags.install --upgrade
```

### html_extract Installation

`html_extract.install` will:
1. Copy html_extract files to `/usr/local/share/html_deltags`
2. Create a Python virtual environment with all dependencies in the installation directory
3. Create a symlink at `/usr/local/bin/html_extract`

Options:
- `--upgrade`: Download the latest version from the repository before installing

Example:
```
# Install normally
sudo ./html_extract.install

# Install using the latest version from the repository
sudo ./html_extract.install --upgrade
```

Root access is required for installation.

## Usage

### html_deltags Usage

As a script:

    html_deltags [options] [input_file]

#### Arguments:

    input_file      Path to HTML file to be detagged.
                    Reads from stdin if not provided.

#### Options:

    -O|--output filename
        Output file for detagged HTML.
        Defaults to stdout.

    -d|--delete tag[,tag,tag]
        HTML tags to remove, as a comma-separated list.
        Multiple -d options allowed.
        Example: ... -d script,link,meta ...
        
    -D|--delete-common
        Add common tags to delete list in optimal order: doctype,head,header,footer,nav,
        iframe,svg,script,style,noscript,comments,path,img,button.
        Equivalent to -d with the above tags in this specific order.

    -k|--kw-delete 'tag keyword'
        Remove tags containing specific keywords.
        Specify tag, space, then pattern/keyword.
        Multiple -k options allowed.
        Example: ... -k 'div sometext' ...

    -p|--parser html5lib|lxml|html.parser
        BS4 html parser to use.
        Default: html5lib

    -h|--help
        Display this help message and exit.

### html_extract Usage

As a script:

    html_extract [options] selector [input_file]

#### Arguments:

    selector        CSS-like selector for tags to extract (e.g., 'p', 'section.p', 'head.title').
                    For nested selectors, use dot notation (e.g., 'div.p' for all paragraphs inside divs).
    
    input_file      Path to HTML file to process.
                    Reads from stdin if not provided.

#### Options:

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

    -a|--attributes attr1,attr2,...
        Include specified attributes in output (comma-separated list) or
        filter tags by attributes (show only tags with these attributes).
        Example: -a class,id
        Example: -a name,description (to filter meta tags with name="description")

    -h|--help
        Display this help message and exit.


#### Parsers:
  Each of the parsers has its strengths and weaknesses:

  Speed: lxml is the fastest, followed by html.parser, then html5lib.

  Error Tolerance: html5lib and lxml are more forgiving of bad or broken HTML compared to html.parser.

  Dependencies: html.parser has the advantage of not requiring any external dependencies.

  Standards Conformance: html5lib is best for parsing HTML in a way that's consistent with modern web browsers.

## Examples

### html_deltags Examples:

    html_deltags my.html -d head,comments,nav

    html_deltags -d head,comments,nav < my.html > mynew.html
    
    html_deltags my.html -D -O clean.html

    html_deltags my.html -d head,comments,nav -d svg,path -O mynew.html

    html_deltags my.html -d head,nav -k 'div class="t1"'

As a module:
```python
from html_deltags import html_deltags
...
clean_html = html_deltags(input_source, output, deltags, deltagkws)
...
```

### html_extract Examples:

    html_extract p my.html
    
    html_extract -n -i section.p < my.html > extracted.txt
    
    html_extract div.h2 my.html -O headers.txt
    
    html_extract head.title my.html
    
    html_extract -i -a href a my.html
    
    html_extract -i meta -a name,description my.html
    
    html_extract -r head my.html
    
### html_format Examples:

    html_format my.html
    
    html_format -i 4 my.html -O formatted.html
    
    html_format < messy.html > clean.html
    
    html_format -m my.html -O minified.html

As modules:
```python
# Using html_extract
from html_extract import extract_tag_contents
...
extracted_content = extract_tag_contents(input_source, output, selector, parser, include_tags, compact_output, raw_mode, attributes)
...

# Using html_format
from html_format import format_html
...
formatted_html = format_html(input_source, output, parser, indent, minify)
...
```

## Requirements
- Python 3
- BeautifulSoup4
- Bash 5

## Repository: https://github.com/Open-Technology-Foundation/html_deltags


## Contributing
Contributions, issues, and feature requests are welcome. Check [issues page](https://github.com/Open-Technology-Foundation/html_deltags/issues).

## License
Distributed under the GPL3 License. See `LICENSE` for more information.

## Contact
Project Link: [https://github.com/Open-Technology-Foundation/html_deltags](https://github.com/Open-Technology-Foundation/html_deltags)
