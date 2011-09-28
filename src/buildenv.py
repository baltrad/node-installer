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

Manages the build environment so that arguments, what modules have been
installed etc can be passed around during installation.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-24
'''
import pickle
import os

##
# The build environment class that keeps track of installation specific
# arguments, what modules that has been installed, etc.
#
class buildenv:
  _args={}
  _argsinternal={}
  _installed={}
  _excluded={}
  _ldlibrarypath=""
  _path=""
  _script = None
  _installerpath = None
  
  ##
  # The name of the file containing installed modules
  FILENAME_INSTALLED_MODULES=".installed_modules.dat"
  
  ##
  # The name of the file containing the saved arguments
  FILENAME_SAVED_ARGUMENTS=".arguments.dat"
  
  ##
  # Constructor
  # 
  def __init__(self):
    if os.path.exists(self.FILENAME_INSTALLED_MODULES):
      fp = open(self.FILENAME_INSTALLED_MODULES, 'r')
      self._installed = pickle.load(fp)
    else:
      self._installed = {}
  
  ##
  # Adds an argument
  # @param name: the name of the argument
  # @param value: the value
  # @param onlyaddifnotexist: Only add the argument value if it doesn't exist
  #
  def addArg(self, name, value, onlyaddifnotexist=False):
    if onlyaddifnotexist == False:
      self._args[name] = value
    elif onlyaddifnotexist == True and not self.hasArg(name):
      self._args[name] = value
  
  ##
  # Adds an internal argument that not is not possible
  # to remember.
  # @param name: the name of the argument
  # @param value: the value
  #
  def addArgInternal(self, name, value):
    self._argsinternal[name] = value

  ##
  # Returns the value associated with the specified argument name
  # @param name: the name of the argument
  # @return: the value
  #
  def getArg(self, name):
    if self._argsinternal.has_key(name):
      return self._argsinternal[name]
    else:
      return self._args[name]

  ##
  # Returns if the specified argument exists or not in the build environment
  # @param name: the argument name
  # @return if it exists or not
  def hasArg(self, name):
    if self._argsinternal.has_key(name):
      return True
    else:
      return self._args.has_key(name)

  ##
  # Restore the configuration
  #
  def restore(self):
    if os.path.exists(self.FILENAME_SAVED_ARGUMENTS):
      fp = open(self.FILENAME_SAVED_ARGUMENTS, 'r')
      self._args = pickle.load(fp)
  
  ##
  # Remembers the configuration
  #
  def remember(self):
    fp = open(self.FILENAME_SAVED_ARGUMENTS, 'w')
    pickle.dump(self._args, fp)
    fp.close()
    
  ##
  # Marks a package to be excluded
  # @param name: the name of the package
  #
  def excludeModule(self, name):
    self._excluded[name] = True
  
  ##
  # Returns if the module has been excluded from the build
  # @param name: the name of the package
  #
  def isExcluded(self, name):
    if self._excluded.has_key(name):
      return self._excluded[name]
    return False

  ##
  # Removes a module from the excluded list
  # @param name: the module that should be removed from the exclusion list
  #
  def removeExclude(self, name):
    if self._excluded.has_key(name):
      self._excluded.pop(name)

  ##
  # Expands arguments in str and returns the new string.
  # E.g. if PREFIX has been added as an argument with value /opt/baltrad and then 
  # str is --prefix=${PREFIX} the returned string will be --prefix=/opt/baltrad
  # @param str: the string to expand
  # @return: the expanded string
  #
  def expandArgs(self, str, extras=None):
    from string import Template
    args = self._args.copy()
    if extras != None:
      args.update(extras)
    args.update(self._argsinternal)
    return Template(str).substitute(args)

  ##
  # Adds that name has been installed with specified version
  # @param name: the name of the package
  # @param version: the version of the installed package
  #
  def addInstalled(self, name, version):
    self._installed[name] = version;
    fp = open(self.FILENAME_INSTALLED_MODULES, 'w')
    pickle.dump(self._installed, fp)

  ##
  # Removes information that the specified package has been installed.
  # Can be used to force a reinstallation of a specific module
  # @param name: the name of the package
  #
  def removeInstalled(self, name):
    if self._installed.has_key(name):
      self._installed.pop(name);
    fp = open(self.FILENAME_INSTALLED_MODULES, 'w')
    pickle.dump(self._installed, fp)
  
  ##
  # Returns the version of the installed package (if it has been installed).
  # Otherwise None will be returned
  # @param name: the name of the package
  # @return: version of package or None if it hasn't been installed
  #
  def getInstalled(self, name):
    if self._installed.has_key(name):
      return self._installed[name]
    return None

  ##
  # Sets the ld library path
  # @param path: the ld library path
  def setLdLibraryPath(self, path):
    self._ldlibrarypath = path

  ##
  # Returns the ld library path
  # @return: the ld library path
  def getLdLibraryPath(self):
    return self._ldlibrarypath
  
  ##
  # Sets the system path
  # @param path: the system path
  def setPath(self, path):
    self._path = path

  ##
  # Returns the system path
  # @return: the system path
  def getPath(self):
    return self._path  
  
  ##
  # Sets the node script
  # @param script: the node scripts instance
  #
  def setNodeScript(self, script):
    self._script = script
  
  ##
  # @return: the node scripts instance
  #
  def getNodeScript(self):
    return self._script
  
  ##
  # Sets the installer path
  # @param path: The installer path
  #
  def setInstallerPath(self, path):
    self._installerpath = path
  
  ##
  # @return: the installer path
  #
  def getInstallerPath(self):
    return self._installerpath
  
  ##
  # Removes all information about installed modules
  #
  def removeInstallInformation(self):
    if os.path.exists(self.FILENAME_INSTALLED_MODULES):
      os.remove(self.FILENAME_INSTALLED_MODULES)
    if os.path.exists(self.FILENAME_SAVED_ARGUMENTS):
      os.remove(self.FILENAME_SAVED_ARGUMENTS)
    self._installed = {}
    self._args = {}

  