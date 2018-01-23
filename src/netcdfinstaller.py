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

NETCDF Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2017-12-19
'''
from installer import installer
import os, subprocess, platform, shutil, string
from osenv import osenv
from InstallerException import InstallerException

##
# The NETCDF installer
#
class netcdfinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH"},
                   defaultosenv={"LD_LIBRARY_PATH":""})
    super(netcdfinstaller, self).__init__(pkg, oenv)
  
  ##
  # Returns the cflags
  # @param benv: the build environment
  def get_cflags(self, benv):
    result = "-I\"$TPREFIX/include\""
    if benv.hasArg("ZLIBINC"):
      result = " -I\"%s\""%benv.getArg("ZLIBINC")
    return result

  ##
  # Returns the ldflags
  def get_ldflags(self, benv):
    result = "-L\"$TPREFIX/lib\""
    if benv.hasArg("ZLIBLIB"):
      result = " -L\"%s\""%benv.getArg("ZLIBLIB")
    return result
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    
    # Dont check error code for distclean, it will fail if fresh build
    # so we wait with failing until next call is performed
    subprocess.call("make distclean", shell=True)

    cmd = env.expandArgs("CFLAGS=%s LDFLAGS=%s ./configure --prefix=\"$TPREFIX\""%(self.get_cflags(env), self.get_ldflags(env)))
    ocode = subprocess.call(cmd, shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to configure netcdf"

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to build netcdf"

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install netcdf"
