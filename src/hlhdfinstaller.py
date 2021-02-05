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

HLHDF Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from installer import installer
import os, subprocess, platform, shutil, string
from osenv import osenv
from InstallerException import InstallerException

##
# The Baltrad DB installer
#
class hlhdfinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH"},
                   defaultosenv={"LD_LIBRARY_PATH":""})
    super(hlhdfinstaller, self).__init__(pkg, oenv)
  
  ##
  # Returns the zlib argument
  # @param benv: the build environment
  def get_zlib_arg(self, benv):
    inc = None
    lib = None
    result = None
    if benv.hasArg("ZLIBINC"):
      inc = benv.getArg("ZLIBINC")
    if benv.hasArg("ZLIBLIB"):
      lib = benv.getArg("ZLIBLIB")
  
    if inc != None or lib != None:
      result = "--with-zlib="
      if inc != None:
        result = result + inc
        result = result + ","
      if lib != None:
        result = result + lib
      
    return result
  
  ##
  # Installs the documentation
  # @param env: the build environment
  def _install_doc(self, env):
    pth = env.expandArgs("$PREFIX/doc/hlhdf")
    if os.path.exists("doxygen/doxygen/html"):
      if os.path.exists(pth):
        shutil.rmtree(pth, True)
      shutil.copytree("doxygen/doxygen/html", pth)
  
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

    cmd = "./configure --prefix=\"$PREFIX/hlhdf\""
    if env.hasArg("ENABLE_PY3") and env.getArg("ENABLE_PY3"):
      cmd = cmd + " --enable-py3support"
    cmd = cmd + " --with-hdf5=$TPREFIX/include,$TPREFIX/lib"
    zarg = self.get_zlib_arg(env)
    if zarg != None:
      cmd = "%s %s"%(cmd,zarg)
    
    newcmd = env.expandArgs(cmd)
    
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException("Failed to configure hlhdf")

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to build hlhdf")

    #if platform.machine() == 'x86_64':
    #  ocode = subprocess.call("make test", shell=True)
    #  if ocode != 0:
    #    raise InstallerException("Failed to test hlhdf")      

    ocode = subprocess.call("make doc > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print("Failed to generate HLHDF documentation")
    else:
      self._install_doc(env)

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to install hlhdf")

    python_bin="python"
    if env.hasArg("ENABLE_PY3") and env.getArg("ENABLE_PY3"):
      python_bin="python3"

    # Use the installed pythons site-packages location
    cmd = python_bin + " -c \"import sys;import os;print(os.sep.join([sys.prefix, 'lib', 'python'+sys.version[:3],'site-packages']))\""
    plc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    shutil.copy(env.expandArgs("$PREFIX/hlhdf/hlhdf.pth"), "%s/"%plc.decode('utf-8').strip())
