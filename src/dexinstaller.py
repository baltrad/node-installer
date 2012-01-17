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

DEX Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-11
'''
from installer import installer
import os, subprocess, shutil
from osenv import osenv
from InstallerException import InstallerException

##
# The dex installer
#
class dexinstaller(installer):
  ##
  # Constructor
  # Installs the dex package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      #LD_LIBRARY_PATH=`generate_ld_path` 
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":""})
    super(dexinstaller, self).__init__(pkg, oenv)

  ##
  # Installs the documentation
  # @param env: the build environment
  #
  def _install_doc(self, env):
    pth = env.expandArgs("$PREFIX/doc/dex")
    if os.path.exists("docs"):
      if os.path.exists(pth):
        shutil.rmtree(pth, True)
      shutil.copytree("docs", pth)
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)

    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", env.getLdLibraryPath())
    
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -Dinstall.prefix=$PREFIX -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbeast.path=$PREFIX/beast -Djavahdf.path=$HDFJAVAHOME install"), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install dex"

    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -Dinstall.prefix=$PREFIX -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbeast.path=$PREFIX/beast -Djavahdf.path=$HDFJAVAHOME javadocs > /dev/null 2>&1"), shell=True)
    if ocode != 0:
      print "Failed to generate DEX documentation"
    else:
      self._install_doc(env)


    