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

import os, sys
import shutil
import time
import subprocess

from installer import installer
from InstallerException import InstallerException

class keystoreinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(keystoreinstaller, self).__init__(package, None)
    
  ##
  # Checks if the provided dir exists and if not creates it
  # @param dir: the dir name
  def _createdir(self, dir):
    if not os.path.exists(dir):
      os.mkdir(dir)
    elif not os.path.isdir(dir):
      raise InstallerException, "%s exists but is not a directory"%dir
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    self._createdir(env.expandArgs("$PREFIX/etc"))

    dst = env.expandArgs("$PREFIX/etc/.java-keystore")
    backup = dst + "%s.bak" % time.strftime("%Y%m%dT%H%M%S")
    if os.path.exists(dst):
      shutil.copy(dst, backup)
    
    keystore = None  # The configured keystore if any
    if env.hasArg("KEYSTORE"):
      keystore = env.expandArgs("$KEYSTORE")
      
    if keystore != None and not os.path.exists(keystore):
      raise InstallerException, "Specified erroneous --keystore=.. no such file"

    if keystore != None:
      shutil.copy(keystore, dst)

    genkey = False
    if os.path.exists(dst):
      ocode = subprocess.call(env.expandArgs("keytool -list -v -keystore \"$PREFIX/etc/.java-keystore\" -keypass \"$KEYSTOREPWD\" -storepass \"$KEYSTOREPWD\" -alias $NODENAME"), shell=True)
      if ocode != 0:
        genkey = True
    else:
      genkey = True

    if genkey == True:
      print env.expandArgs("No key with alias = $NODENAME could be found in keystore")
      print "Please answer these questions to get a key generated"
      owner = raw_input("Key owner: ")
      unit = raw_input("Unit: ")
      org = raw_input("Organization: ")
      city = raw_input("City: ")
      country = raw_input("Country: ")
      cc = raw_input("Country code (e.g. PL): ")

      cmd = env.expandArgs("keytool -genkey -alias \"$NODENAME\" -keystore \"$PREFIX/etc/.java-keystore\"" +
                           " -keypass \"$KEYSTOREPWD\" -keyalg DSA -sigalg DSA -validity 1825 "+
                           " -storepass \"$KEYSTOREPWD\" -dname \"cn=%s, ou=%s, o=%s, l=%s, st=%s, c=%s\""%(owner, unit, org, city, country, cc))

      print ""
      print cmd
      print ""

      ocode = subprocess.call(cmd, shell=True)
      if ocode != 0:
        raise InstallerException, "failed to generate keystore alias"

    ocode = subprocess.call(env.expandArgs("keytool -list -v -keystore \"$PREFIX/etc/.java-keystore\" -keypass \"$KEYSTOREPWD\" -storepass \"$KEYSTOREPWD\" -alias $NODENAME"), shell=True)
    if ocode != 0:
      raise InstallerException, "Could not define wanted keystore alias.."
    else:
      print env.expandArgs("Keystore available in $PREFIX/etc/.java-keystore")

