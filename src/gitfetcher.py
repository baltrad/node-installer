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
  
  ##
  # Constructor
  # @param url: the url of the resource to be fetched from the git repository
  # @param tag: the specific tag that should be checked out
  # @param branch: the specific branch that should be checked out 
  #
  def __init__(self, url, tag=None, branch=None):
    super(fetcher, self).__init__()
    n = url[string.rfind(url, ":")+1:]
    self.project = n[:string.rfind(n,".git")]
    self.url = url
    self.tag = tag
    self.branch = branch
  
  
  ##
  # Fetches the code from the git repository
  # @param env: the build environment
  # @return the directory name of the package that has been fetched
  #
  def dofetch(self, env=None):
    if not os.path.exists(self.project):
      code = subprocess.call("git clone %s"%self.url, shell=True)
      if code != 0:
        raise InstallerException, "Failed to fetch %s from repository"%self.url
    
    cdir = os.getcwd()
    os.chdir(self.project)
    
    code = subprocess.call("git pull %s HEAD:master"%self.url, shell=True)
    if code != 0:
      raise InstallerException, "Failed to update %s from repository"%self.url
    
    if self.branch != None:
      a=subprocess.Popen("git branch -l", shell=True, stdout=subprocess.PIPE)
      output=a.communicate()[0]
      if a.returncode != 0:
        os.chdir(cdir)
        raise InstallerException, "Failed to list branches %s from repository"%self.url
      
      if re.search("^\s*%s\s*$"%self.branch, output, flags=re.MULTILINE) == None:
        code = subprocess.call("git checkout -b %s remotes/origin/%s"%(self.branch,self.branch))
        if code != 0:
          os.chdir(cdir)
          raise InstallerException, "Failed to fetch branch %s from repository"%self.branch       
      code = subprocess.call("git checkout %s"%(self.branch))
      if code != 0:
        os.chdir(cdir)
        raise InstallerException, "Failed to checkout branch %s"%self.branch
    
    if self.tag != None:
      code = subprocess.call("git checkout %s"%(self.tag), shell=True)
      if code != 0:
        os.chdir(cdir)
        raise InstallerException, "Failed to checkout tag %s from repository"%self.tag       

    os.chdir(cdir)
    
    return self.project

  ##
  # Cleans up the git repository
  # @param env: The build environment
  #
  def doclean(self, env=None):
    if os.path.exists(self.project):
      if self.project not in [".", "..", "/", "../", "./"]:
        shutil.rmtree(self.project, True)

  ##
  # Fetches the offline content related to the git repository. Will generate a 
  # tar ball for the fetched software
  # @param env: the build environment
  #
  def dofetch_offline_content(self, env=None):
    raise InstallerException, "dofetch_offline_content not implemented in gitfetcher yet"
    #self.dofetch(env)
    # git archive --format=tar --prefix="hlhdf-$HLHDF_VERSION/" HEAD | gzip > "$TMP_BLT_DIR/baltrad-core/hlhdf-$HLHDF_VERSION.tgz"
