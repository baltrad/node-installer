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

Manages access to the OS environment variables. Its usage is mostly to
be able to take snapshots of environment variables, then set new ones
and finally be able to restore the environment back to the time of the
snapshot.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-25
'''
import os

##
# The OS environment class
class osenv:
  ## The environment variables to be set
  _env = {}
  ## An optional function that can manage optional/dynamic environment variables
  # The function signature must be dict func(benv, envdict).
  _foptionalenv = None
  
  ## This can be used to set default values in the os environment
  # if they don't exist. 
  _defaultosenv = None
  
  ## The environment variables that will be processed
  _variables = {}
  
  ## The current snapshot to be restored
  _snapshot = {}
  
  ##
  # Constructor
  # @param env: A dictionary of os environment variables that should be set. These environment values
  # can both refer to build environment variables as well as OS environment variables.
  # The environment variable expansion is performed as a two-step rocket. First the
  # build environment variables are expanded and then the os environment variables. To achieve this
  # behaviour you will have to double escape the os environment variables.
  # For example: "${PREFIX}:$${LD_LIBRARY_PATH}" would first expand the build environment variable
  # PREFIX and then the OS environment variable LD_LIBRARY_PATH.
  # @param env: the os environment variables
  # @param foptionalenv: is a function that takes buildenv and the environment dictionary as argument and
  #    returns a dictionary of optional variables the returned environment variables will override the
  #    ones defined in env
  # 
  def __init__(self, env, foptionalenv=None, defaultosenv=None):
    self._env = env
    self._foptionalenv = foptionalenv
    self._defaultosenv = defaultosenv
    
  ##
  # Builds a list of all variables that should be set
  # @param benv: the build environment
  # @return: the merged dictionary
  def _buildvariabledict(self, benv = None):
    variables = {}
    if self._foptionalenv != None:
      variables = self._foptionalenv(benv, self._env)
    for key in self._env.keys():
      if not variables.has_key(key):
        variables[key] = self._env[key]
    return variables
     
    
  ##
  # Takes a snapshot of the environment variables that should be updated
  #
  def snapshot(self, benv=None):
    self._variables = self._buildvariabledict(benv)
    self._snapshot = {}
    for key in self._variables.keys():
      if os.environ.has_key(key):
        self._snapshot[key] = os.environ[key]
      else:
        self._snapshot[key] = None

  ##
  # Returns the value of the snapshot variable
  # @param key: the name of the variable
  # @return: the value
  def getSnapshotVariable(self, key):
    return self._snapshot[key]
  

  ##
  # Sets the default os environment variables if they haven't
  # already got a value.
  # @return: the keys to be reset
  #
  def _setDefaultOsEnvironment(self):
    oskeys = []
    if self._defaultosenv != None:
      for k in self._defaultosenv.keys():
        if not k in os.environ.keys():
          oskeys.append(k)
          os.environ[k] = self._defaultosenv[k]
    return oskeys

  ##
  # Deletes the provided keys from the os environment
  # @param oskeys: a list of keys
  #
  def _deleteKeysFromOsEnvironment(self, oskeys):
    for k in oskeys:
      if os.environ.has_key(k):
        del os.environ[k]

  ##
  # Expands the string with the OS environment variables
  # @param v: the string to be expanded
  # @return: the expanded string
  #
  def expandEnvironment(self, v):
    from string import Template
    oskeys = self._setDefaultOsEnvironment()
    try:
      return Template(v).substitute(os.environ)
    finally:
      self._deleteKeysFromOsEnvironment(oskeys)
  
  ##
  # Sets the os environment by first using the provided build environment variables and
  # then the os environment variables. Will perform a snapshot prior setting the
  # environment variables.
  # @param benv: the build environment
  #
  def setenv(self, benv):
    self.snapshot(benv)
    for key in self._variables.keys():
      v = benv.expandArgs(self._variables[key])
      os.environ[key] = self.expandEnvironment(v)
  
  ##
  # Restores the os environment variable values prior the snapshot
  #
  def restore(self):
    for key in self._snapshot.keys():
      if self._snapshot[key] != None:
        os.environ[key] = self._snapshot[key]
      else:
        if os.environ.has_key(key):
          os.environ.pop(key)

  ##
  # If you want to force an environment variable to be set
  # and later restored, you can use this method. However,
  # you must still have registered the variable name
  # in the dictionary of snapshotted environment variables abd
  # a snapshot must have been performed.
  # @param benv: the build environment
  # @param name: the name of the environment variable
  # @param value: the value, Behaves like explained in the constructor
  #
  def setEnvironmentVariable(self, benv, name, value):
    if name in self._snapshot.keys():
      v = benv.expandArgs(value)
      os.environ[name] = self.expandEnvironment(v)
    else:
      raise Exception,"Environment variable %s has not been snapshotted"%name