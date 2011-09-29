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

Fetcher for machine dependent fetching, it will fetch software for either
i386 or x86_64 archs and eventually other OS but that is experimental.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-07
'''
from fetcher import fetcher
from InstallerException import InstallerException

##
# The machine dependent fetcher class
class machinefetcher(fetcher):
  url = None
  fname = None
  
  ##
  # Constructor. The fetchers is a dictionary with machine name as key
  #  and fetcher for that specific machine. The machine is determined by
  #  platform.machine.
  # @param fetchers: the dictionary of fetchers
  #
  def __init__(self, fetchers={}):
    super(machinefetcher, self).__init__()
    self._fetchers = fetchers
  
  ##
  # Executes the machine dependent fetcher
  # @param env: the build environment
  # @return the result of the machine specific fetcher
  #
  def dofetch(self, env=None):
    import platform
    m = platform.machine()
    if self._fetchers.has_key(m):
      return self._fetchers[m].fetch(env)
    raise InstallerException, "Unsupported machine type %s"%m

  ##
  # Cleans up the machine dependent fetcher
  # @param env: the build environment
  #
  def doclean(self, env=None):
    for k in self._fetchers.keys():
      self._fetchers[k].clean(env)
  
  ##
  # Executes all fetchers regardless of machine type
  # @param env: the build environment
  #  
  def dofetch_offline_content(self, env=None):
    for k in self._fetchers.keys():
      self._fetchers[k].dofetch_offline_content(env)
