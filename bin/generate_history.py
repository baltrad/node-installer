#!/usr/bin/env python
import os
import getopt
import re
import sys

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(FILE_DIR, "../src"))

import gitutil
from gitfetcher import gitfetcher
from nodedefinition import PACKAGES, NODE_REPOSITORY
from buildenv import buildenv

PACKAGES_DIR = os.path.join(FILE_DIR, "../packages")

_USAGE = """
Usage: %(prog)s <since git revision> [<to git revision>]

example:
  %(prog)s v0.5.0
  %(prog)s v0.4.0 v0.5.0
""" 

def usage():
  print _USAGE % {"prog": sys.argv[0]}

def node_versions_from_rev(rev):
  code = gitutil.git_show(rev + ":src/node_versions.py")
  d = {}
  exec code in d
  return d["versions"]

def package_path(pkg):
  return os.path.normpath(
    os.path.join(
      PACKAGES_DIR,
      gitfetcher(NODE_REPOSITORY[pkg].geturi()).project
    )
  )

def fetch_package(pkg, env):
  os.chdir(PACKAGES_DIR)
  gitfetcher(NODE_REPOSITORY[pkg].geturi()).fetch(env)


def find_tickets(log):
  tickets = re.findall(r"^\s+Ticket \d+.*$", log, re.M)
  return [ticket.strip("\n\r ") for ticket in tickets]

def print_changes(repo_path, since_rev, until_rev):
  os.chdir(repo_path)
  if since_rev != until_rev:
    log = gitutil.git_log(since_rev, until_rev)
    tickets = find_tickets(log)
    if not tickets:
      print "   Changed but no tickets resolved"
    else:
      for ticket in tickets:
        print "  ", ticket
  else:
    print "   No changes"

def main():
  if len(sys.argv) >= 2:
    since_rev = sys.argv[1]
  else:
    since_rev = gitutil.git_describe(abbrev=0)

  if len(sys.argv) >= 3:
    until_rev = gitutil.git_describe(sys.argv[2])
  else:
    until_rev = gitutil.git_describe()
  
  env = buildenv()
  env.addUniqueArg("GITREPO", "gitosis@git.baltrad.eu")

  for pkg in PACKAGES:
    fetch_package(pkg, env)

  print "Changes from", since_rev, "to", until_rev, "\n"
  
  print "node-installer:"
  print_changes(FILE_DIR, since_rev, until_rev);
  print ""

  since_node_revs = node_versions_from_rev(since_rev)
  until_node_revs = node_versions_from_rev(until_rev)

  for pkg in PACKAGES:
    print pkg + ":"
    print_changes(
      package_path(pkg),
      since_node_revs.get(pkg),
      until_node_revs.get(pkg)
    )
    print ""

if __name__ == "__main__":
  main()
