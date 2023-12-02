
# `html_deltags` - html tag-remover/minimizer

Remove specific tags from a html file or stream and output detagged/minified HTML to file or stdout.

`html_deltags` is a Python module and Shell script designed to detag, normalize and 'minify' HTML documents. Removes specified HTML tags, including those containing certain keywords, and comments, streamlining further analysis of remaining HTML using clean input.

## Features
- Removes specified HTML tags and comments from an HTML document.
- Can target and delete tags based on contained keywords.
- Flexible usage as both a standalone script and an importable Python module.

## Installation

    git clone https://github.com/Open-Technology-Foundation/html_deltags.git && sudo html_deltags/html_deltags.install

`html_deltags.install` will copy html_deltags files to `/usr/share/html_deltags` and create symlink `/usr/local/bin/html_deltags`.

Root access is required for installation.

## Usage
  As a script:

    html_deltags [options] [input_file]

### Arguments:

    input_file      Path to HTML file to be detagged.
                    Reads from stdin if not provided.


### Options:

Options:

    -O|--output filename
        Output file for detagged HTML.
        Defaults to stdout.

    -d|--delete tag[,tag,tag]
        HTML tags to remove, as a comma-separated list.
        Multiple -d options allowed.
        Example: ... -d script,link,meta ...

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


#### Parsers:
  Each of the parsers has its strengths and weaknesses:

  Speed: lxml is the fastest, followed by html.parser, then html5lib.

  Error Tolerance: html5lib and lxml are more forgiving of bad or broken HTML compared to html.parser.

  Dependencies: html.parser has the advantage of not requiring any external dependencies.

  Standards Conformance: html5lib is best for parsing HTML in a way that's consistent with modern web browsers.

## Examples:

    html_deltags my.html -d head,comments,nav

    html_deltags -d head,comments,nav < my.html > mynew.html

    html_deltags my.html -d head,comments,nav -d svg,path -O mynew.html

    html_deltags my.html -d head,nav -k 'div class="t1"'

As a module:
```python
from html_deltags import html_deltags
...
clean_html = html_deltags(input_source, output, deltags, deltagkws)
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
