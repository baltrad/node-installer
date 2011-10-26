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

Installer super class. All installers should inherit this class to get
basic installation support.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-25
'''
from InstallerException import InstallerException
import os

##
# Installer class
class installer(object):
  _package = None
  _oenv = None
  
  ##
  # Constructor
  # @param package: the package to be installed
  # @param oenv: os environment variables
  #
  def __init__(self, package, oenv = None):
    self._package = package
    self._oenv = oenv
  
  ##
  # Installer method. Will ensure that a if a package should be installed the sub
  # class will get a call to doinstall and also that upon success it is marked
  # as installed for future references.
  # @param env: the build environment (buildenv)
  # @param forcerebuild: Forces a rebuild regardless if it has been installed or not
  # @return: if package has been installed or not
  #
  def install(self, env, forcerebuild=False):
    name = self.package().name()
    version = self.package().version()
    remembered = self.package().isremembered()
    
    installed = False
    if not env.isExcluded(name):
      if forcerebuild:
        env.removeInstalled(name)

      if remembered == False or forcerebuild or env.getInstalled(name) != version:
        cdir = os.getcwd()
        try:
          if self.osenvironment() != None:
            self.osenvironment().setenv(env)
          self.doinstall(env)
        finally:
          os.chdir(cdir)        
          if self.osenvironment() != None:
            self.osenvironment().restore()
        if remembered:
          env.addInstalled(name, version)
        installed = True
      else:
        print "Package %s - %s already installed skipping."%(name, version)
    else:
      print "Package %s - %s excluded from build."%(name, version)
    return installed
  
  ##
  # Subclasses should implement this function
  # @param env: the build environment
  #
  def doinstall(self, env):
    raise InstallerException, "Installer does not implement doinstall"
  
  ##
  # Returns the package that this installer will install
  # @return: the package
  #
  def package(self):
    return self._package

  ##
  # Returns the os environment
  # @return the os environment
  def osenvironment(self):
    return self._oenv
  
  ##
  # Executes the packages fetch_offline_content
  # @param env: the build environment
  #  
  def fetch_offline_content(self, env=None):
    self.package().fetch_offline_content(env)

  ##
  # Executes the package cleanup
  # @param env: the build environment
  #
  def clean(self, env=None):
    self.package().clean(env)
