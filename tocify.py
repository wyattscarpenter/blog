#!/usr/bin/env python3

"""This script merely appends a line of formatted text to the readme.md in this folder; it is probably of no general interest to anyone."""

from datetime import date
from os import path
from sys import stderr
import argparse

parser = argparse.ArgumentParser(
  prog='tocify',
  description=__doc__,
  epilog="""Example usage: tocify.py test.txt "example post" -pf ===> 2024-01-01: 𝝅𝝋 example post: <https://wyattscarpenter.github.io/blog/test.txt>"""
)

parser.add_argument('basename.ext', type=str, help="The file name that will be used in the url. Do not include the rest of the path. Example: foo.txt. Note: you should be able to tab-complete this, which is why it's the first argument. Also, tocify will check that this file exists, to help you prevent typos.")
parser.add_argument('"Title Of Post"', type=str, help="The post title that will be used in the listing. Example: 'On The Fooing Of Foos: Or, How I Learned To Give Up And Love The Foo'. Note: you will probably have to quote this argument, in your shell.")
parser.add_argument('-p', '-pi', '--pi', '-political', '--political', '-pol', '--pol', '-π', action='store_true', help="Mark the post with a 𝝅. Note: only ever used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")
parser.add_argument('-f', '-phi', '--phi', '-philosophy', '--philosophy', '-phil', '--phil', '-φ', action='store_true', help="Mark the post with a 𝝋, indicating it is about philosophy. Note: sometimes used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")

a = vars(parser.parse_args())

file_to_which_to_append = "readme.md"
print(a)
print("file_to_which_to_append:", file_to_which_to_append)
if not path.isfile(a['basename.ext']):
  print(f"Error: {a['basename.ext']} is not an existing file, which is required.", file=stderr)
  exit(-1)
cool_string: str = f"""\n{date.today()}: \
{'𝝅𝝋 ' if a['pi'] and a['phi'] else '𝝅 ' if a['pi'] else '𝝋 ' if a['phi'] else ''}\
{a['"Title Of Post"']}: <https://wyattscarpenter.github.io/blog/{a['basename.ext']}>\n"""
print(cool_string)

with open(file_to_which_to_append, "a", encoding="utf-8", newline='\n') as f:
  f.write(cool_string)
