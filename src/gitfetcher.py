'''
Copyright (C) 2011 Swedish Meteorological and Hydrological Institute, SMHI,

This file is part of baltrad node installer.

This is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this software.  If not, see <http://www.gnu.org/licenses/>.
------------------------------------------------------------------------*/

The GIT fetcher.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-21
'''
import string
import subprocess
import os
import re
from InstallerException import InstallerException
from fetcher import fetcher
import shutil

##
# The git fetcher class
#
class gitfetcher(fetcher):
  url = None
  tag = None
  project = None
  offlinename = None
  
  ##
  # Constructor
  # @param url: the url of the resource to be fetched from the git repository
  # @param tag: the specific tag that should be checked out
  # @param branch: the specific branch that should be checked out 
  #
  def __init__(self, url, tag=None, branch=None):
    super(fetcher, self).__init__()
    n = url[url.rfind("/")+1:]
    self.project = n[:n.rfind(".git")]
    self.url = url
    self.tag = tag
    self.branch = branch
    self.offlinename =  "%s-%s"%(self.project, self.tag)
  
  ##
  # Executes the git clone/pull sequence
  def _fetchgit(self, env):
    url = env.expandArgs(self.url)
    if not os.path.exists(self.project):
      code = subprocess.call("git clone %s"%url, shell=True)
      if code != 0:
        raise InstallerException("Failed to fetch %s from repository"%url)
    
    cdir = os.getcwd()
    os.chdir(self.project)
    
    code = subprocess.call("git pull %s HEAD:master"%url, shell=True)
    if code != 0:
      raise InstallerException("Failed to update %s from repository"%url)
    
    if self.branch != None:
      a=subprocess.Popen("git branch -l", shell=True, stdout=subprocess.PIPE)
      output=a.communicate()[0]
      if a.returncode != 0:
        os.chdir(cdir)
        raise InstallerException("Failed to list branches %s from repository"%url)
      
      if re.search("^\s*%s\s*$"%self.branch, output, flags=re.MULTILINE) == None:
        code = subprocess.call("git checkout -b %s remotes/origin/%s"%(self.branch,self.branch))
        if code != 0:
          os.chdir(cdir)
          raise InstallerException("Failed to fetch branch %s from repository"%self.branch)       
      code = subprocess.call("git checkout %s"%(self.branch))
      if code != 0:
        os.chdir(cdir)
        raise InstallerException("Failed to checkout branch %s"%self.branch)
    
    if self.tag != None:
      code = subprocess.call("git checkout %s"%(self.tag), shell=True)
      if code != 0:
        os.chdir(cdir)
        raise InstallerException("Failed to checkout tag %s from repository"%self.tag)       

    os.chdir(cdir)
    
    return self.project
  
  ##
  # Fetches the code from the git repository
  # @param package: the package to fetch
  # @param env: the build environment
  # @return the directory name of the package that has been fetched
  #
  def dofetch(self, package, env=None):
    if env.hasArg("INSTALL_OFFLINE") and env.getArg("INSTALL_OFFLINE") == True:
      code = subprocess.call("tar -xvzf %s.tgz"%self.offlinename, shell=True)
      if code != 0:
        raise InstallerException("Could not unpack %s.tgz, but offline was specified"%self.offlinename)
      return self.offlinename
    
    return self._fetchgit(env)

  ##
  # Cleans up the git repository
  # @param package: the package to clean
  # @param env: The build environment
  #
  def doclean(self, package, env=None):
    if os.path.exists(self.project):
      if self.project not in [".", "..", "/", "../", "./"]:
        shutil.rmtree(self.project, True)
    if os.path.exists("%s.tgz"%self.offlinename):
      os.remove("%s.tgz"%self.offlinename)
    if os.path.exists(self.offlinename):
      if self.offlinename not in [".", "..", "/", "../", "./"]:
        shutil.rmtree(self.offlinename, True)

  ##
  # Fetches the offline content related to the git repository. Will generate a 
  # tar ball for the fetched software
  # @param package: the package to fetch
  # @param env: the build environment
  #
  def dofetch_offline_content(self, package, env=None):
    self._fetchgit(env)

    cdir = os.getcwd()
    os.chdir(self.project)
    
    ipath = "%s/packages"%env.getInstallerPath()
    
    code = subprocess.call("git archive --format=tar --prefix=\"%s/\" HEAD | gzip > \"%s/%s.tgz\""%(self.offlinename,ipath,self.offlinename), shell=True)
    if code != 0:
      os.chdir(cdir)
      raise InstallerException("Failed to create archive from git repository %s"%self.project)
    os.chdir(cdir)    

    if self.project not in [".", "..", "/", "../", "./"]:
      shutil.rmtree(self.project, True)
    if os.path.exists(self.offlinename):
      if self.offlinename not in [".", "..", "/", "../", "./"]:
        shutil.rmtree(self.offlinename, True)
      
