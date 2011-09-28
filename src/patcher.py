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

Fetcher class that depends on a fetcher that returns a tar-ball and then
unpacks it.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-09-27
'''
import subprocess
from InstallerException import InstallerException
from fetcher import fetcher
import os

##
# The patcher (fetcher). This will patch the result from the fetcher
#
class patcher(fetcher):
  _fetcher = None
  _patches = []
  
  ##
  # Constructor
  # @param fetcher: the fetcher
  # @param patches: a list of strings identifying the patch names
  #
  def __init__(self, fetcher, patches = []):
    self._fetcher = fetcher
    if patches != None:
      self._patches = patches
  
  ##
  # Executes the fetcher and then patches the software in the resulting directory
  # @param env: the build environment
  # @return the directory that was the result of this fetch
  #
  def dofetch(self, env=None):
    cdir = os.getcwd()
    
    dirname = self._fetcher.fetch(env)
    os.chdir(dirname)
    
    print "PATCHING %s"%`self._patches`
    for patch in self._patches:
      code = subprocess.call("patch -p0 < %s/patches/%s"%(env.getInstallerPath(),patch), shell=True)
      if code != 0:
        os.chdir(cdir)
        raise InstallerException, "Failed to apply patch %s"%patch
    
    os.chdir(cdir)
    return dirname
  
  ##
  # Executes the fetchers clean up
  # @param env: the build environment
  #
  def doclean(self, env=None):
    self._fetcher.clean(env)
