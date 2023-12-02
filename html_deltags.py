#!/usr/bin/env python
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
      Remove tags containing specific keywords.
      Specify tag, space, then pattern/keyword.
      Multiple -k options allowed.
      Example: ... -k 'div sometext' ...
  -p|--parser html5lib|lxml|html.parser
      BS4 html parser to use.
      Default: html5lib
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

Requires:
  Python >= 3.10
  pip:beautifulsoup4 >= 4.10.0
  Bash >= 5.0

Repository:
  https://github.com/Open-Technology-Foundation/html_deltags
"""

from bs4 import BeautifulSoup, Comment

def html_deltags(input_source, output, deltags:list, deltagkws, parser:str='html5lib'):
  """
  Detags/minimizes a HTML document by removing specified tags and comments.

  Args:
  input_source (str or file-like object): The source of the HTML content. Can be a file path or stdin.

  output (str or file-like object): The destination for the detagged HTML content. Can be a file path or stdout.

  deltags (list of str): Tags to remove from the HTML content.

  deltagkws (list of tuples): Tags + keyword to remove from the HTML content. Must be in the format (tag, pattern).

  This function reads the HTML content from input_source, removes the specified tags and comments, and writes the detagged/minimized HTML to output.
  """
  # Read input
  if isinstance(input_source, str):
    with open(input_source, 'r', encoding='utf-8') as file:
      soup = BeautifulSoup(file, parser)
  else:
    soup = BeautifulSoup(input_source, parser)

  tag_name:str = ''
  kw:str = ''

  # Remove all instances of a specific tag
  for Tag in deltags:
    if Tag in ('comments', '!--'):
      # Find and remove all comment tags
      comments = soup.find_all(string=lambda text: isinstance(text, Comment))
      for comment in comments:
        comment.extract()
    else:
      for tag in soup.find_all(Tag):
        tag.decompose()

  # Remove all instances of a specific tag that contains a keyword
  tag_kw:tuple = ('','')
  for tag_kw in deltagkws:
    tag_name, kw = tag_kw
    for tag in soup.find_all(lambda t: t.name == tag_name and t.get('class') and kw in ' '.join(t.get('class'))):
      tag.decompose()

  # Minify
  minified_html = soup.prettify(encoding=None, formatter="minimal")
  # Output
  if isinstance(output, str):
    with open(output, 'w', encoding='utf-8') as file:
      file.write(minified_html)
  else:
    output.write(minified_html)

# If running as a shell script... ============================================
if __name__ == '__main__':
  import os
  import sys
  # Initialize default values
  input_source = None
  _output_file  = sys.stdout
  _deltags:list = []
  _deltagkws    = []
  _arg:str      = ''
  _arr:list     = []
  _parser:str   = 'html5lib'

  # Command line arguments processing
  _index:int = 1
  while _index < len(sys.argv):
    _arg = sys.argv[_index]
    if _arg in ('-h', '--help'):
      print(__doc__)
      sys.exit(0)

    # output to file
    if _arg in ('-O', '--output'):
      if _index + 1 >= len(sys.argv):
        print(f"{os.path.basename(__file__)}: error: '{_arg}' option requires an argument", file=sys.stderr)
        sys.exit(1)
      _output_file = sys.argv[_index + 1]
      _index += 1

    # parser
    elif _arg in ('-p', '--parser'):
      if _index + 1 >= len(sys.argv):
        print(f"{os.path.basename(__file__)}: error: '{_arg}' option requires an argument", file=sys.stderr)
        sys.exit(1)
      _parser = sys.argv[_index + 1]
      _index += 1

    # tags delete
    elif _arg in ('-d', '--delete'):
      if _index + 1 >= len(sys.argv):
        print(f"{os.path.basename(__file__)}: error: '{_arg}' option requires an argument", file=sys.stderr)
        sys.exit(1)
      _deltags += sys.argv[_index + 1].split(',')
      _index += 1

    # tag+keyword delete
    elif _arg in ('-k', '--kw-delete'):
      if _index + 1 >= len(sys.argv):
        print(f"{os.path.basename(__file__)}: error: '{_arg}' option requires an argument", file=sys.stderr)
        sys.exit(1)
      _arr = sys.argv[_index + 1].split(' ')
      _deltagkws.append((_arr[0], ' '.join(_arr[1:])))
      _index += 1

    # input source
    elif input_source is None:
      input_source = _arg
      if not os.path.isfile(input_source):
        print(f"{os.path.basename(__file__)}: error: '{input_source}' does not exist.", file=sys.stderr)
        sys.exit(1)
    else:
      print(f"{os.path.basename(__file__)}: error: unexpected argument '{_arg}'", file=sys.stderr)
      sys.exit(1)
    _index += 1

  if input_source is None:
    input_source = sys.stdin

  html_deltags(input_source, _output_file, _deltags, _deltagkws, _parser)

#fin
#    -h|--help
#    -O|--output
#    -p|--parser
#    -d|--delete
#    -k|--kw-delete
