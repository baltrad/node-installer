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

The overall installer that performs the installation, dependency checking et al..

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-02
'''
import os
import subprocess
import tempfile
import bltversion

class node_installer:
  _installers = []
  _rebuild = []
  ##
  # Constructor
  # @param installers: the list of installers to be executed
  # @param rebuild: If some modules should be rebuilt, add them as a list of names here.
  def __init__(self, installers, rebuild=None):
    self._installers = installers
    if rebuild != None:
      self._rebuild = rebuild
    
  ##
  # Performs the installation of the software
  # @param benv: the build environment
  def install(self, benv):
    mlen = len(self._installers)
    for i in range(mlen):
      m = self._installers[i]
      pkg = m.package()
      name = pkg.name()
      
      if m.install(benv, name in self._rebuild):
        # If we come here, installation has been performed, verify if
        # there are any dependent modules that needs to be (re)installed
        for j in range(i+1,mlen):
          pkname = self._installers[j].package().name()
          if name in self._installers[j].package().dependencies():
            benv.removeInstalled(pkname)

  ##
  # Cleans up all downloaded resources
  # @param benv: the build environment
  def clean(self, benv):
    mlen = len(self._installers)
    for i in range(mlen):
      m = self._installers[i]
      m.clean(benv)
    benv.removeInstallInformation()
  
  ##
  # Fetches all packages so that it is possible to run
  # an 'offline' installation.
  #
  def fetch_offline_content(self, benv):
    mlen = len(self._installers)
    for i in range(mlen):
      m = self._installers[i]
      m.fetch_offline_content(benv)
    
  ##
  #
  def create_offline_tarball(self, benv):
    self.fetch_offline_content(benv)
    bltversion.set_offline_node_version()
    node_version = bltversion.get_node_version()
    target = os.path.join(
        tempfile.gettempdir(),
        "node-installer-%s.tar.gz" % node_version
    )
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.check_call([
        "tar",
        "-cvpzf", target,
        "--exclude-vcs",
        "--exclude='*.pyc'",
        "--transform=s/^./node-installer-%s/" % node_version,
        "--show-transformed-names",
        "."
    ])
