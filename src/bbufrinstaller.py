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

BBUFR Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-12-16
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The BBUFR installer
#
class bbufrinstaller(installer):
  ##
  # Constructor
  # Installs the bbufr package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH"},
                   defaultosenv={"LD_LIBRARY_PATH":""})
    super(bbufrinstaller, self).__init__(pkg, oenv)
  
  ##
  # Returns the zlib arguments
  # @param benv: the build environment
  def get_zlib_args(self, benv):
    inc = None
    lib = None
    if benv.hasArg("ZLIBINC"):
      inc = benv.getArg("ZLIBINC")
    if benv.hasArg("ZLIBLIB"):
      lib = benv.getArg("ZLIBLIB")

    if inc != None and inc != "":
      inc = "-I%s"%inc
    if lib != None and lib != "":
      lib = "-L%s"%lib
    
    return (inc, lib)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    cdir = self.package().fetch(env)
    
    os.chdir(cdir)

    # Dont check error code for distclean, it will fail if fresh build
    # so we wait with failing until next call is performed
    subprocess.call("make distclean", shell=True)

    cmd = "./configure --prefix=\"$PREFIX/bbufr\""
    cflags = "-I$TPREFIX/include"
    ldflags = "-L$TPREFIX/lib"
    zinc,zlib = self.get_zlib_args(env)
    if zinc != None:
      cflags="%s %s"%(cflags, zinc)
    if zlib != None:
      ldflags="%s %s"%(ldflags, zlib)
    cflags = "CFLAGS=\"%s\""%cflags
    ldflags = "LDFLAGS=\"%s\""%ldflags

    cmd = "%s %s %s"%(cflags,ldflags,cmd)
    
    newcmd = env.expandArgs(cmd)
    
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException("Failed to configure bbufr")

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to build bbufr")

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to install bbufr")

 
    