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
import os, subprocess, string, shutil
from osenv import osenv
from InstallerException import InstallerException


class bropoinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH",
                    "EXPATARG":"$TPREFIX",
                    "HLDIR":"$PREFIX/hlhdf",
                    "PROJ4ROOT":"$TPREFIX",
                    "RAVEROOT":"$PREFIX/rave"}, # RAVEROOT is the installation path....
                    defaultosenv={"LD_LIBRARY_PATH":""})
      
    super(bropoinstaller, self).__init__(pkg, oenv)

  ##
  # Installs the documentation
  # @param env: the build environment
  def _install_doc(self, env):
    pth = env.expandArgs("$PREFIX/doc/bropo")
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
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),self.osenvironment().getSnapshotVariable("LD_LIBRARY_PATH")))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),self.osenvironment().getSnapshotVariable("PATH")))
    
    # Dont check error code for distclean, it will fail if fresh build
    # so we wait with failing until next call is performed
    subprocess.call("make distclean", shell=True)

    cmd = "./configure --prefix=\"$PREFIX/bropo\" --with-rave=\"$PREFIX/rave\""
    newcmd = env.expandArgs(cmd)
    
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException("Failed to configure bropo")

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to build bropo")

    ocode = subprocess.call("make test", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to test bropo")      

    ocode = subprocess.call("make doc > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print("Failed to generate BROPO documentation")
    else:
      self._install_doc(env)

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException("Failed to install bropo")
    
    python_bin="python"
    if env.hasArg("ENABLE_PY3") and env.getArg("ENABLE_PY3"):
      python_bin="python3"

    cmd = python_bin + " -c \"import sys;import os;print(os.sep.join([sys.prefix, 'lib', 'python'+sys.version[:3],'site-packages']))\""
    plc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    foutname = "%s/bropo.pth"%plc.decode('utf-8').strip()

    try:
      fp = open(foutname, "w")
      fp.write(env.expandArgs("$PREFIX/bropo/share/bropo/pyropo"))
      fp.close()
    except Exception as e:
      raise InstallerException("Failed to generate bropo.pth in python site-packages, %s"%str(e.__str__()))
