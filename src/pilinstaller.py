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

PIL installer.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-26
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The optional environment variable that should be set for
# PIL.
def pil_optional_environment(benv, envdic):
  result = {}
  if benv.hasArg("ZLIBLIB") and benv.getArg("ZLIBLIB") != None and benv.getArg("ZLIBLIB") != "":
    if envdic.has_key("LD_LIBRARY_PATH"):
      result["LD_LIBRARY_PATH"] = "$ZLIBLIB:%s"%envdic.get("LD_LIBRARY_PATH")
  return result

##
# The PIL installer
#
class pilinstaller(installer):
  ##
  # Constructor
  # Installs the package containing PIL. Could have included package in this class
  # as well but right now its a matter of getting it to work.
  # @param package: the pil package
  #
  def __init__(self, package):
    env = osenv({"LD_LIBRARY_PATH":"$TPREFIX/lib"}, pil_optional_environment)
    super(pilinstaller, self).__init__(package, env)
  
  ##
  # Generates a modified setup script and returns the new script
  # @param env: the build environment
  # @return the name of the generated setup script
  #
  def generate_setupscript(self, env):
    zinc = "%s/include"%env.getArg("TPREFIX")
    zlib = "%s/lib"%env.getArg("TPREFIX")
    
    if env.hasArg("ZLIBLIB") or env.hasArg("ZLIBINC"):
      zinc=""
      zlib=""
      if env.hasArg("ZLIBLIB") and env.getArg("ZLIBLIB") != None:
        zlib = env.getArg("ZLIBLIB")
      if env.hasArg("ZLIBINC") and env.getArg("ZLIBINC") != None:
        zinc = env.getArg("ZLIBINC")
    
    ifp = open("setup.py", "r")
    ofp = open("tmpsetup.py", "w")
    inlines = ifp.readlines()
    for l in inlines:
      tl = l
      if tl.find("ZLIB_ROOT = None") >= 0:
        tl = "ZLIB_ROOT = \"%s\",\"%s\"\n"%(zlib,zinc)
      ofp.write(tl)
    ifp.close()
    ofp.close()
    return "tmpsetup.py"
  
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    name = self.package().name()
    version = self.package().version()
    
    os.chdir(dir)
    
    setupscript="setup.py"
    if not env.isExcluded("ZLIB"):
      setupscript = self.generate_setupscript(env)

    cmdstr = env.expandArgs("\"$TPREFIX/bin/python\" %s install" % setupscript)
    code = subprocess.call(cmdstr, shell=True)
    if code != 0:
      raise InstallerException, "Failed to execute command %s for %s (%s)"%(cmdstr, name,version)
    