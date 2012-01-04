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

RAVE Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-10-05
'''
from installer import installer
import os, subprocess, string
from osenv import osenv
from InstallerException import InstallerException


class beambinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH"},
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(beambinstaller, self).__init__(pkg, oenv)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),self.osenvironment().getSnapshotVariable("LD_LIBRARY_PATH")))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),self.osenvironment().getSnapshotVariable("PATH")))
    
    # Dont check error code for distclean, it will fail if fresh build
    # so we wait with failing until next call is performed
    subprocess.call("make distclean", shell=True)

    cmd = "./configure --prefix=\"$PREFIX/beamb\" --with-rave=\"$PREFIX/rave\""
    newcmd = env.expandArgs(cmd)
    
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to configure beamb"

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to build beamb"

    ocode = subprocess.call("make test", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to test beamb"      

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install beamb"