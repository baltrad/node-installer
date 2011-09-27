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

RAVE gmap Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-11
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The RAVE Google map installer
#
class ravegmapinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$PREFIX/rave/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$PREFIX/rave/lib:$$LD_LIBRARY_PATH"})
      
    super(ravegmapinstaller, self).__init__(pkg, oenv)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),os.environ["LD_LIBRARY_PATH"]))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),os.environ["PATH"]))

    ocode = subprocess.call(env.expandArgs("python setup.py install --prefix=\"$PREFIX\""), shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install"
    
    ocode = subprocess.call("rave_pgf stop >> /dev/null 2>&1", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to stop rave pgf"
    
    if os.path.exists("tmpreg.py"):
      os.unlink("tmpreg.py")
    fp = open("tmpreg.py", "w")
    fp.write(env.expandArgs("""
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="$PREFIX/rave/etc/rave_pgf_registry.xml")
a.deregister('se.smhi.rave.creategmapimage')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile')
"""))
    fp.close()

    try:    
      ocode = subprocess.call("python tmpreg.py", shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to register google maps plugin in rave"
    finally:
      if os.path.exists("tmpreg.py"):   
        os.unlink("tmpreg.py")
