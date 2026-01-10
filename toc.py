#!/usr/bin/env python3

"""This script merely appends a line of formatted text to the readme.md in this folder; it is probably of no general interest to anyone."""

from datetime import date, timedelta
from os import path
from sys import stderr, argv
import argparse
from subprocess import run
import re

parser = argparse.ArgumentParser(
  description=__doc__,
  epilog="""Example usage: toc test.txt "example post" -pi -phi ===> 2024-01-01: 𝝅𝝋 [Example Post](test.txt)"""
)

def warn(*args: object) -> None:
  print(*args, file=stderr)

def dateformat(s: str) -> date:
  try:
    return date.fromisoformat(s)
  except ValueError:
    try:
      return date.today() + timedelta(days=int(s))
    except ValueError:
      raise ValueError(f"I could not interpret ‘{s}’ as date nor a relative offset. Try something like ‘2024-03-31’ or ‘3’.")

file_to_which_to_append: str = "readme.md"

pf_usage: str = "used to mark a post as 𝝅𝝋, political philosophy; you may do that with (for example) -pf"

parser.add_argument('basename.ext', type=str, help="The file name that will be used in the url. Do not include the rest of the path. Example: foo.txt. Note: you should be able to tab-complete this, which is why it's the first argument. Also, if the file doesn't exist, toc will create it for you. SPECIAL CIRCUMSTANCE: if basename.ext is .[ext] then \"Title Of Post\" will be converted to an appropriate file name a la title_of_post.[ext] and the file will be created (in which case, the file already existing is an error); in such cases, ext defaults to txt if not provided.")
parser.add_argument('"Title Of Post"', type=str, help="The post title that will be used in the listing. Example: 'On The Fooing Of Foos: Or, How I Learned To Give Up And Love The Foo'. Note: you will probably have to quote this argument, in your shell. The title will be converted to initial caps, the capitalization style in the example I just gave.")
parser.add_argument('-d', '-date', '--date', type=dateformat, help="The date the post will be dated as. Defaults to the output of date.today() if not specified. It should be given in 2024-03-31 format. The argument to this flag is validated against python's datetime's ISO 8601 recognizer: https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat . Additionally, supplying a bare integer will use date.today() plus (or minus) that many days. I like to provide arguments like ‘+3’ because they are valid, but that is just another way to spell ‘3’ as far as Python is concerned.") # It would be more ergonomic to use dateparser.parse here, thus making my user life easier, but currently this script has no deps outside of the stdlib, which is nice.
parser.add_argument('-p', '-pi', '--pi', '-π', action='store_true', help="Mark the post with a 𝝅. Note: only ever "+pf_usage)
parser.add_argument('-f', '-phi', '--phi', '-φ', action='store_true', help="Mark the post with a 𝝋, indicating it is about philosophy. Note: sometimes "+pf_usage)
parser.add_argument('-n', '-nono', '-dry-run', '--nono', '--dry-run', action='store_true', help="Exit the program before we make any changes, thereby doing nothing, in order to merely test the program.")
parser.add_argument('-dont-git', '--dont-git', action='store_true', help=f"Don't git add the changes (the newly-created file and {file_to_which_to_append}). Furthermore, unless this flag is specified, this script will attempt to add a pre-commit hook to the .git/hooks folder (although it will not overwrite an extant pre-commit file.")
parser.add_argument('-check', '--check', action='store_true', help=f"Instead of doing anything else, cross-reference the contents of {file_to_which_to_append} and git ls-files and exit with an error if there are files listed in the former that are missing from the latter.")

print("file_to_which_to_append:", file_to_which_to_append)

def capture_stdout(program: list[str]) -> list[str]:
  """Captures the stdout of a program as utf-8, checks the return code of that process, and returns a list of the stdout splitting on ascii NUL (\0)"""
  result = run(program, capture_output=True, encoding="utf-8")
  result.check_returncode()
  return result.stdout.split('\0')

if '--check' in argv or '-check' in argv: #due to the way argparse works, this is the best way to do this.
  # Get the list of files from git (if used in pre-commit, these are the files in the new commit, btw, the staged changes are included)
  git_files = capture_stdout(['git', 'ls-files', '-z', ':(glob)*']) # the final argument means only list the files in the base directory, not recursive.
  # Check the contents of the readme
  readme_files: list[str] = []
  with open(file_to_which_to_append, "r", encoding="utf-8", newline="\n") as file:
    for line in file:
      if m := re.match(r"^(.*?): 𝝅?𝝋? ?\[(.*)\]\((.*?)\)\s*?$", line):
        readme_files += m.group(3), #lol at this syntax
  missing_files = [file for file in readme_files if file not in git_files and file+".md" not in git_files] # There is a special case due to how github pages treats md files by default
  if missing_files:
    warn("These files are not found in git files (the cache/stage of git)! (Are you sure you have git add/rm/mv'd properly?):")
    for mf in missing_files:
      warn("  ", mf)
    exit(4)
  else:
    warn(f"No problems found with {file_to_which_to_append} vis-a-vis what files are in the git ls-files.")
  additionally_expected_files = [ # files we expect to be here, but aren't entries in the readme
    'readme.md',
    'README.txt',
    '.gitignore',
    'generate_rss.py',
    'toc',
    'toc.bat',
    'toc.py'
  ]
  expected_files = additionally_expected_files + readme_files
  unexpectedly_found_files = [file for file in git_files if file not in expected_files and file.removesuffix(".md") not in readme_files and file.removesuffix(".comments.txt")+".txt" not in readme_files]
  if unexpectedly_found_files:
    warn(f"These files were unexpectedly found in the main directory, even though {file_to_which_to_append} does not contemplate them:")
    for uff in unexpectedly_found_files:
      warn("  ", uff)
  exit(0) # if you got all the way here you must be fine.

a = vars(parser.parse_args())
print(a)

a['"Title Of Post"'] = "".join( x.capitalize() for x in re.findall(r"[-\w']+|\W+", a['"Title Of Post"']) )

special_circumstance = False
if a['basename.ext'][0] == '.':
  special_circumstance = True
  old_ext = a['basename.ext']
  if a['basename.ext'] == '.':
    a['basename.ext'] = '.txt'
  a['basename.ext'] = ( "_".join(re.findall(r"[-\w]+", a['"Title Of Post"'].lower())) ) + a['basename.ext'] #This assumes you want sort-of-url-style document titles. Which, you know, probably you do.
  print(f"Due to the special circumstance of basename.ext starting with . ( {old_ext} ) I'm creating a new file by the name of {a['basename.ext']} instead of requiring it to be a pre-existing file.")
  if path.isfile(a['basename.ext']):
    print(f"Error: {a['basename.ext']} is an extant file, which is forbidden.", file=stderr)
    exit(-1)

if not a['date']:
  a['date'] = date.today()

pf: str = '𝝅'*a['pi'] + '𝝋'*a['phi'] + ' '*(a['pi'] or a['phi'])
cool_string: str = f"""\n{a['date']}: {pf}[{a['"Title Of Post"']}]({a['basename.ext']})\n"""
print(cool_string)

if a['nono']:
  print('Dry-run ("nono" run) completed; no changes made.')
  exit()

with open(file_to_which_to_append, "a", encoding="utf-8", newline='\n') as f:
  f.write(cool_string)
if not path.isfile(a['basename.ext']):
  with open(a['basename.ext'], "a", encoding="utf-8", newline='\n') as f:
    f.write("")

if not a["dont_git"]:
  run(["git", "add", a['basename.ext'], file_to_which_to_append])
  # Add the git pre-commit hook to the git hooks folder
  p = ".git/hooks/pre-commit"
  p_payload = "#!/bin/sh\ngit diff --check && ./toc.py --check" #You have to add a #!/bin/sh to this, or chmod it, for git to use it right, I think.
  try:
    with open(p, 'x', encoding="utf-8", newline='\n') as f:
      f.write(p_payload)
    print(f"Created new git hook '{p_payload}' at {p}.")
  except FileExistsError:
    print(f"{p} already exists, so I am not trying to overwrite it.")
