import subprocess

def git_describe(tag=None, abbrev=None):
  args = ["git", "describe"]
  if tag:
    args.append(tag)
  if abbrev:
    args.append("--abbrev=%d" % abbrev)
  proc = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode != 0:
    raise Exception("`git describe` failed: %s" % stderr.strip("\n\r "))
  return stdout.strip("\n\r ")

def git_show(obj):
  args = ["git", "show", obj]
  proc = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode != 0:
    raise Exception("`git show` failed: %s" % stderr.strip("\n\r "))
  return stdout.strip("\n\r ")

def git_log(since="", until=""):
  args = ["git", "log"]
  if since or until:
    args.append("%s..%s" % (since, until))
  proc = subprocess.Popen(" ".join(args), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = proc.communicate()
  if proc.returncode != 0:
    raise Exception("`git log` failed: %s" % stderr.strip("\n\r "))
  return stdout.strip("\n\r ")
