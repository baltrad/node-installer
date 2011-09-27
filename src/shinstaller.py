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

Basically a do whatever you want installer that executes a shell command.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-25
'''
from installer import installer
import os, subprocess
from InstallerException import InstallerException

##
# The shell installer class
#
class shinstaller(installer):
  _cmd = None
  
  ##
  # Constructor
  # @param package: the package to install
  # @param cmd: the shell command to be executed, command will be expanded with arguments from build environment
  #
  def __init__(self,package,cmd,env=None):
    super(shinstaller, self).__init__(package, env)
    self._cmd = cmd
  
  ##
  # Executes the install step.
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    name = self.package().name()
    version = self.package().version()
    
    os.chdir(dir)
    cmdstr = env.expandArgs(self._cmd)
    code = subprocess.call("%s"%cmdstr, shell=True)
    if code != 0:
      raise InstallerException, "Failed to execute command %s for %s (%s)"%(cmdstr, name,version)
    