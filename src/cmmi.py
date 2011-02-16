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

configure, make, make test and make install installer.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-20
'''
import os
import subprocess
from InstallerException import InstallerException
from installer import installer

##
# Configure, make, make install installer class
class cmmi(installer):
  _args = ""
  _test = False
  _install = False
  _foptionalarg = None
  _fpostinstall = None
  _foptionaltest = None
  
  ##
  # Constructor
  # @param package: the package to be installed
  # @param args: any arguments that should be passed during configure phase, expands arguments
  # @param dotest: if make test should be run or not
  # @param doinstall: if make install should be run or not
  # @param env: os environment variables 
  # @param foptionalarg: This is a functioncall that will be executed with the build environment in order to see if any
  #   particular argument should be appended to the argument string
  #
  def __init__(self, package, args="", dotest=False, doinstall=False, env=None, foptionalarg=None, foptionaltest=None, fpostinstall=None):
    super(cmmi, self).__init__(package, env)
    self._args = args
    self._test = dotest
    self._install = doinstall
    self._foptionalarg = foptionalarg
    self._foptionaltest = foptionaltest
    self._fpostinstall = fpostinstall
  
  ##
  # Performs the actual installation sequence
  # @param env: the build environment
  # @raise InstallerException: if any problem occurs during installation
  # 
  def doinstall(self, env):
    dir = self.package().fetch(env)
    name = self.package().name()
    version = self.package().version()
    
    os.chdir(dir)
    args = self._args
    if self._foptionalarg != None:
      extraarg = self._foptionalarg(env)
      if extraarg != None:
        args = "%s %s"%(args, extraarg)

    argstr = env.expandArgs(args)
    code = subprocess.call("./configure %s"%argstr, shell=True)
    if code != 0:
      raise InstallerException, "Failed to configure software %s (%s)"%(name,version)
    
    code = subprocess.call("make", shell=True)
    if code != 0:
      raise InstallerException, "Failed to compile software %s (%s)"%(name,version)

    if self._test == True:
      if self._foptionaltest == None or self._foptionaltest(env) == True:
        code = subprocess.call("make test", shell=True)
        if code != 0:
          raise InstallerException, "Failed to test software %s (%s)"%(name,version)
    
    if self._install == True:
      code = subprocess.call("make install", shell=True)
      if code != 0:
        raise InstallerException, "Failed to install software %s (%s)"%(name,version)

    if self._fpostinstall != None:
      self._fpostinstall(env)
