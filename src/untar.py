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
@date 2011-01-20
'''
import subprocess
from InstallerException import InstallerException
from fetcher import fetcher

##
# The untar fetcher
#
class untar(fetcher):
  fetcher = None
  dirname = None
  compressed = True
  
  ##
  # Constructor
  # @param fetcher: the fetcher that returns a tar ball
  # @param dirname: the directory name that will be the outcome when extracting the tarball
  # @param compressed: If this tar ball is compressed or not
  #  
  def __init__(self, fetcher, dirname, compressed=True):
    super(untar, self).__init__()
    self.fetcher = fetcher
    self.dirname = dirname
    self.compressed = compressed
  
  ##
  # Fetches and extracts the tar ball
  # @param env: the build environment
  # @return: the directory that was the result of this tar extraction
  #
  def dofetch(self, env=None):
    filename = self.fetcher.fetch(env)
    args = ""
    if self.compressed == True:
      args = "-xvzf"
    else:
      args = "-xvf"

    code = subprocess.call("tar %s %s"%(args,filename), shell=True)
    if code != 0:
      raise InstallerException, "Failed to extract software %s"%self.name
    
    return self.dirname