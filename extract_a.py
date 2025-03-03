#!/usr/bin/env python3

from html.parser import HTMLParser
import sys

class LinkExtractor(HTMLParser):
  def __init__(self):
    super().__init__()
    self.links = []
    self.current_link = ''
    self.is_a_tag = False

  def handle_starttag(self, tag, attrs):
    if tag == 'a':
      self.is_a_tag = True
      attrs_dict = dict(attrs)
      self.current_link = attrs_dict.get('href', '')

  def handle_endtag(self, tag):
    if tag == 'a':
      self.is_a_tag = False

  def handle_data(self, data):
    if self.is_a_tag:
      text = data.strip()
      if text:
        self.links.append((self.current_link, text))

if __name__ == '__main__':
  html_content = sys.stdin.read()
  parser = LinkExtractor()
  parser.feed(html_content)
  for href, text in parser.links:
    text = text.replace('\r\n', '\\n').replace('\r', '\\n').replace('\n', '\\n')
    print(f"Link: [{text}]({href})")

#fin
