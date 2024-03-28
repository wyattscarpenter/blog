#!/usr/bin/env python3

"""This script merely appends a line of formatted text to the readme.md in this folder; it is probably of no general interest to anyone."""

from datetime import date
from os import path
from sys import stderr, argv
import argparse
from subprocess import run
import re

parser = argparse.ArgumentParser(
  prog='tocify',
  description=__doc__,
  epilog="""Example usage: tocify.py test.txt "example post" -pf ===> 2024-01-01: 𝝅𝝋 example post: <https://wyattscarpenter.github.io/blog/test.txt>"""
)

file_to_which_to_append = "readme.md"

parser.add_argument('basename.ext', type=str, help="The file name that will be used in the url. Do not include the rest of the path. Example: foo.txt. Note: you should be able to tab-complete this, which is why it's the first argument. Also, tocify will check that this file exists, to help you prevent typos. SPECIAL CIRCUMSTANCE: if basename.ext is .[ext] then \"Title Of Post\" will be converted to an appropriate file name a la title_of_post.[ext] and the file will be created (in which case, the file already existing is an error); in such cases, ext defaults to txt if not provided.")
parser.add_argument('"Title Of Post"', type=str, help="The post title that will be used in the listing. Example: 'On The Fooing Of Foos: Or, How I Learned To Give Up And Love The Foo'. Note: you will probably have to quote this argument, in your shell.")
parser.add_argument('-d', '-date', '--date', type=date.fromisoformat, help="The date the post will be dated as. Defaults to the output of date.today() if not specified. It should be given in 2024-03-31 format. The argument to this flag is validated against python's datetime's ISO 8601 recognizer: https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat")
parser.add_argument('-p', '-pi', '--pi', '-political', '--political', '-pol', '--pol', '-π', action='store_true', help="Mark the post with a 𝝅. Note: only ever used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")
parser.add_argument('-f', '-phi', '--phi', '-philosophy', '--philosophy', '-phil', '--phil', '-φ', action='store_true', help="Mark the post with a 𝝋, indicating it is about philosophy. Note: sometimes used to mark a post as 𝝅𝝋, political philosophy; you may do that with -pf")
parser.add_argument('-n', '-nono', '-dry-run', '--nono', '--dry-run', action='store_true', help="Exit the program before we write the file, thereby doing nothing, in order to merely test the program.")
parser.add_argument('-dont-git', '--dont-git', action='store_true', help=f"Don't git add the changes (the newly-created file and {file_to_which_to_append}). Furthermore, unless this flag is specified, this script will attempt to add a pre-commit hook to the .git/hooks folder (although it will not overwrite an extant pre-commit file.")
parser.add_argument('-check', '--check', action='store_true', help=f"Instead of doing anything else, cross-reference the contents of {file_to_which_to_append} and git ls-files and exit with an error if there are files listed in the former that are missing from the latter.")

print("file_to_which_to_append:", file_to_which_to_append)

def capture_stdout(program: list[str]) -> list[str]:
  result = run(program, capture_output=True, encoding="utf-8")
  result.check_returncode()
  return result.stdout.splitlines()

if '--check' in argv or '-check' in argv: #due to the way argparse works, this is the best way to do this.
  number_of_errors = 0
  # Get the list of files from git (these are the files in the new commit, btw, the staged changes are included)
  try:
    git_files = capture_stdout(['git', 'ls-files'])
  except FileNotFoundError:
    # (As it happens, I never expect to need this forbidden jutsu in this part of the code, because --check is mostly run from a git hook, which is thus already in WSL for me. But, anyway...)
    print("git wasn't found on the path, so I assume YOU are ME, and use the forbidden jutsu: git.bat", file=stderr)
    git_files = capture_stdout(['git.bat', 'ls-files'])
  # Check the contents of the readme
  with open(file_to_which_to_append, "r", encoding="utf-8", newline="\n") as file:
    for i in file:
      m = re.match("^(.*?): (.*) <?(https?://.*)/(.*?)>?\s*?$", i)
      if m:
        if m.group(4) not in git_files:
          print(f"{m.group(4)} not found in git files! (The cache/stage of git.) Are you sure you git add'd it? Are you sure you didn't git rm it? Are you sure that if you moved it, you git mv'd it?", file=stderr)
          number_of_errors += 1
  if not number_of_errors:
    print(f"No problems found with {file_to_which_to_append} vis-a-vis what files are in the git ls-files.", file=stderr)
  exit(number_of_errors)

a = vars(parser.parse_args())
print(a)

special_circumstance = False
if a['basename.ext'][0] == '.':
  special_circumstance = True
  old_ext = a['basename.ext']
  if a['basename.ext'] == '.':
    a['basename.ext'] = '.txt'
  a['basename.ext'] = ( "_".join(re.findall("[-\w]+", a['"Title Of Post"'].lower())) ) + a['basename.ext'] #This assumes you want sort-of-url-style document titles. Which, you know, probably you do.
  print(f"Due to the special circumstance of basename.ext starting with . ( {old_ext} ) I'm creating a new file by the name of {a['basename.ext']} instead of requiring it to be a pre-existing file.")
  if path.isfile(a['basename.ext']):
    print(f"Error: {a['basename.ext']} is an existing file, which is forbidden.", file=stderr)
    exit(-1)
else:
  if not path.isfile(a['basename.ext']):
    print(f"Error: {a['basename.ext']} is not an existing file, which is required.", file=stderr)
    exit(-1)

if not a['date']:
  a['date'] = date.today()

cool_string: str = f"""\n{a['date']}: \
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

if not a["dont_git"]:
  # git add the files
  try:
    run(["git", "add", a['basename.ext'], file_to_which_to_append])
  except FileNotFoundError:
    print("git wasn't found on the path, so I assume YOU are ME, and use the forbidden jutsu: git.bat", file=stderr)
    run(["git.bat", "add", a['basename.ext'], file_to_which_to_append])
  # Add the git pre-commit hook to the git hooks folder
  p = ".git/hooks/pre-commit"
  p_payload = "git diff --check && ./tocify.py --check"
  try:
    with open(p, 'x', encoding="utf-8", newline='\n') as f:
      f.write(p_payload)
    print(f"Created new git hook '{p_payload}' at {p}.")
  except FileExistsError:
    print(f"{p} already exists, so I am not trying to overwrite it.")
