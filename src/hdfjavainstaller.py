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

Installer for hdf java and hdf java setup

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-21
'''
from installer import installer
import shutil, os, stat

##
# Used by path walker to change mode for all files
# @param arg: the permission as bitmasked stat value, e.g. stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH
# @param dirname: the directory name
# @param fnames: the file names
#
def _recursive_chmod(arg, dirname, fnames):
  os.chmod(dirname, arg)
  for file in fnames:
    os.chmod(os.path.join(dirname, file), arg)

##
# The hdf java installer class
#
class hdfjavainstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(hdfjavainstaller, self).__init__(package, None)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch()
    
    shutil.rmtree(env.expandArgs("$TPREFIX/hdf-java"), True)
    
    os.path.walk(dir, _recursive_chmod, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    
    shutil.move(dir, env.expandArgs("$TPREFIX/hdf-java"))


class hdfjavasetupinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(hdfjavasetupinstaller, self).__init__(package, None)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    files = ["jhdf5.jar", "jhdf5obj.jar", "jhdf.jar", "jhdfobj.jar"]
    if env.getInstalled("TOMCAT") != None:
      for f in files:
        src = env.expandArgs("$HDFJAVAHOME/lib/%s"%f)
        dst = env.expandArgs("$TPREFIX/tomcat/lib/")
        shutil.copy(src, dst)
