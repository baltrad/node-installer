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

Baltrad DB Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The Baltrad DB installer
#
class bdbinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME", 
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$PREFIX/hlhdf/lib:$$LD_LIBRARY_PATH"})
    super(bdbinstaller, self).__init__(pkg, oenv)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    
    ocode = subprocess.call("./waf distclean", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to perform distclean"
    
    cmd = "./waf configure --prefix=$PREFIX/baltrad-db"
    cmd = cmd + " --jdk_dir=$JDKHOME"
    cmd = cmd + " --hlhdf_dir=$PREFIX/hlhdf"
    cmd = cmd + " --hdf5_dir=$TPREFIX"
    cmd = cmd + " --boost_dir=$TPREFIX"
    cmd = cmd + " --pqxx_dir=$TPREFIX"
    cmd = cmd + " --build_java=yes"
    cmd = cmd + " --build_tests=yes"
    cmd = cmd + " --build_bdbtool=yes"
    cmd = cmd + " --build_bdbfs=$BUILD_BDBFS"
    cmd = cmd + " --ant=$TPREFIX/ant/bin/ant"
    cmd = cmd + " --swig=$TPREFIX/bin/swig"
    
    newcmd = env.expandArgs(cmd)
    
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to configure bdb"

    ocode = subprocess.call("./waf build", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to build bdb"

    ocode = subprocess.call("./waf test", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to test bdb"

    ocode = subprocess.call("./waf install", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install bdb"
    