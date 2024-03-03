#!/usr/bin/env python3

"""This script merely appends a line of formatted text to the readme.md in this folder; it is probably of no general interest to anyone."""

from datetime import date
from os import path
from sys import stderr
import argparse
from subprocess import run

parser = argparse.ArgumentParser(
  prog='tocify',
  description=__doc__,
  epilog="""Example usage: tocify.py test.txt "example post" -pf ===> 2024-01-01: 𝝅𝝋 example post: <https://wyattscarpenter.github.io/blog/test.txt>"""
)

file_to_which_to_append = "readme.md"
rss_file = "rss.xml"

parser.add_argument('basename.ext', type=str, help="The file name that will be used in the url. Do not include the rest of the path. Example: foo.txt. Note: you should be able to tab-complete this, which is why it's the first argument. Also, tocify will check that this file exists, to help you prevent typos. SPECIAL CIRCUMSTANCE: if basename.ext is .[ext] then \"Title Of Post\" will be converted to an appropriate file name a la title_of_post.[ext] and the file will be created (in which case, the file already existing is an error); in such cases, ext defaults to txt if not provided.")
parser.add_argument('"Title Of Post"', type=str, help="The post title that will be used in the listing. Example: 'On The Fooing Of Foos: Or, How I Learned To Give Up And Love The Foo'. Note: you will probably have to quote this argument, in your shell.")
parser.add_argument('-p', '-pi', '--pi', '-political', '--political', '-pol', '--pol', '-π', action='store_true', help="Mark the post with a 𝝅. Note: only ever used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")
parser.add_argument('-f', '-phi', '--phi', '-philosophy', '--philosophy', '-phil', '--phil', '-φ', action='store_true', help="Mark the post with a 𝝋, indicating it is about philosophy. Note: sometimes used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")
parser.add_argument('-n', '-nono', '-dry-run', '--nono', '--dry-run', action='store_true', help="Exit the program before we write the file, thereby doing nothing, in order to merely test the program.")
parser.add_argument('-dont-rss', action='store_true', help=f"Don't refresh {rss_file} after updating {file_to_which_to_append}.")
parser.add_argument('-dont-git', action='store_true', help=f"Don't git add the changes (the newly-created file, {file_to_which_to_append}, and {rss_file}.)")
a = vars(parser.parse_args())
print(a)
print("file_to_which_to_append:", file_to_which_to_append)

special_circumstance = False
if a['basename.ext'][0] == '.':
  special_circumstance = True
  old_ext = a['basename.ext']
  if a['basename.ext'] == '.':
    a['basename.ext'] = '.txt'
  a['basename.ext'] = a['"Title Of Post"'].lower().replace(" ", "_").replace(":","") + a['basename.ext'] #This does not cover all the NTFS-forbidden characters, but maybe it should, someday.
  print(f"Due to the special circumstance of basename.ext starting with . ( {old_ext} ) I'm creating a new file by the name of {a['basename.ext']} instead of requiring it to be a pre-existing file.")
  if path.isfile(a['basename.ext']):
    print(f"Error: {a['basename.ext']} is an existing file, which is forbidden.", file=stderr)
    exit(-1)
else:
  if not path.isfile(a['basename.ext']):
    print(f"Error: {a['basename.ext']} is not an existing file, which is required.", file=stderr)
    exit(-1)

cool_string: str = f"""\n{date.today()}: \
{'𝝅𝝋 ' if a['pi'] and a['phi'] else '𝝅 ' if a['pi'] else '𝝋 ' if a['phi'] else ''}\
{a['"Title Of Post"']} <https://wyattscarpenter.github.io/blog/{a['basename.ext']}>\n"""
print(cool_string)

if a['nono']:
  exit()

with open(file_to_which_to_append, "a", encoding="utf-8", newline='\n') as f:
  f.write(cool_string)
if special_circumstance:
  with open(a['basename.ext'], "a", encoding="utf-8", newline='\n') as f:
    f.write("")

if not a["dont_rss"]:
  import generate_rss

if not a["dont_git"]:
  try:
    run(["git", "add", a['basename.ext'], file_to_which_to_append, rss_file])
  except FileNotFoundError:
    print("git wasn't found on the path, so I assume YOU are ME, and use the forbidden jutsu: git.bat", file=stderr)
    run(["git.bat", "add", a['basename.ext'], file_to_which_to_append, rss_file])
