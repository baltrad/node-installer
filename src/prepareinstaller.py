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

This is the preparation step. The previously installed system is stopped.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2012-01-05
'''
from installer import installer
import subprocess, os, time

##
# The prepare installer
class prepareinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(prepareinstaller, self).__init__(package, None)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    pth = env.expandArgs("$PREFIX/bin/bltnode")
    if os.path.exists(pth):
      try:
        subprocess.call("%s --all stop"%pth, shell=True)
      except:
        print("Could not stop running node")
      time.sleep(1)
      