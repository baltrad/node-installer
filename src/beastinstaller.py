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

Beast Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The Beast installer
#
class beastinstaller(installer):
  ##
  # Constructor
  # Installs the beast package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":""})
    super(beastinstaller, self).__init__(pkg, oenv)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)

    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", env.getLdLibraryPath())
    
    ocode = subprocess.call([env.expandArgs(arg) for arg in [
        "$TPREFIX/ant/bin/ant",
        "-Dprefix=$PREFIX",
        "-Dbaltraddb.path=$PREFIX/baltrad-db",
        "-Dbaltraddb.bin.path=$PREFIX/baltrad-db/bin",
        "install",
    ]])
    if ocode != 0:
      raise InstallerException("Failed to install beast")
    
    # We use beasts document installer and just change prefix to the doc-root
    #
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant "+
                                           " -Dprefix=$PREFIX/doc -Dbaltraddb.path=$PREFIX/baltrad-db"+
                                           " -Dbaltraddb.bin.path=$PREFIX/baltrad-db/bin"+
                                           " install-doc > /dev/null 2>&1"), shell=True)
    if ocode != 0:
      print("Failed to generate BEAST documentation")

