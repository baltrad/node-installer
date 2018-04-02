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

Node configuration

'''

import os, subprocess
import shutil
import time
from osenv import osenv
from InstallerException import InstallerException

from installer import installer

class raveconfiginstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$PREFIX/rave/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$PREFIX/rave/lib:$$LD_LIBRARY_PATH"},
                    defaultosenv={"LD_LIBRARY_PATH":""})
    
    super(raveconfiginstaller, self).__init__(package, oenv)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    if not env.isExcluded("RAVE"):
      self._create_quality_registry(env)
    
  ##
  # Creates the quality registry for the various quality plugins that
  # belongs to the different modules
  # @param env: the build environment
  #
  def _create_quality_registry(self, env):
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),os.environ["LD_LIBRARY_PATH"]))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),os.environ["PATH"]))
        
    env.getNodeScript().stop(rave=True)
    
    fp = open("tmpreg.py", "w")
    fp.write(env.expandArgs("""
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("$PREFIX/rave/etc/rave_pgf_quality_registry.xml")
a.remove_plugin("ropo")
a.remove_plugin("beamb")
"""))
    if not env.isExcluded("BROPO"):
      fp.write(env.expandArgs("""
a.add_plugin("ropo", "ropo_quality_plugin", "ropo_quality_plugin")
"""))
    if not env.isExcluded("BEAMB"):
      fp.write(env.expandArgs("""
a.add_plugin("beamb", "beamb_quality_plugin", "beamb_quality_plugin")
"""))
    fp.write(env.expandArgs("""
a.save("$PREFIX/rave/etc/rave_pgf_quality_registry.xml")
"""))
    fp.close()
    try:    
      ocode = subprocess.call("python tmpreg.py", shell=True)
      if ocode != 0:
        raise InstallerException("Failed to register quality plugins in rave")
    finally:
      if os.path.exists("tmpreg.py"):   
        os.unlink("tmpreg.py")

      