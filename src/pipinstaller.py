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

install packages using PIP
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The Baltrad DB installer
#
class pipinstaller(installer):
  ##
  # Constructor
  #
  # @param pkg the package to install
  # @param pypi_name package name in PYPI, if it differs from package.name()
  # @param pip_path path to the pip executable
  # @param quiet if True, pass '--quiet' to pip
  #
  def __init__(self, pkg, pypi_name=None,
               pip_path="$TPREFIX/bin/pip", quiet=True):
    super(pipinstaller, self).__init__(pkg)
    if not pypi_name:
        pypi_name = pkg.name()
    self._pypi_name = pypi_name
    self._pip_path = pip_path
    self._quiet = quiet
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    pip = env.expandArgs(self._pip_path)

    args = [pip, "install"]
    if self._quiet:
        args.append("--quiet")
    args.append("%s == %s" % (self._pypi_name, self.package().version()))

    print " ".join(args)
    ocode = subprocess.call(args)
    if ocode != 0:
      raise InstallerException(
        "Failed to install '%s' using pip" % self._pypi_name
      )
