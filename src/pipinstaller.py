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
  # @param pip_path path to the pip executable
  # @param quiet if True, pass '--quiet' to pip
  #
  def __init__(self, pkg, quiet=True, oenv=None):
    super(pipinstaller, self).__init__(pkg, oenv)
    if not hasattr(pkg, "pypi_name"):
      self._pypi_name = pkg.name()
    else:
      self._pypi_name = pkg.pypi_name
    self._pip_path = "$TPREFIX/bin/pip"
    self._quiet = quiet
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    pip = env.expandArgs(self._pip_path)
    if env.hasArg("ENABLE_PY3"):
      pip = env.expandArgs("$TPREFIX/bin/pip3")
    pkg_dir = os.path.join(
      env.getInstallerPath(),
      "packages",
      self.package().name(),
    )

    args = [pip, "install"]
    # args.append("--build=%s" % pkg_dir)  #Removed from PIP
    if _is_offline_install(env):
      args.append("--no-download")
    if self._quiet:
      args.append("--quiet")
    args.append("%s == %s" % (self._pypi_name, self.package().version()))

    print(" ".join(args))
    ocode = subprocess.call(args)
    if ocode != 0:
      raise InstallerException(
        "Failed to install '%s' using pip. You might need to set the environment variable http_proxy." % self._pypi_name
      )

def _is_offline_install(env):
  return env.hasArg("INSTALL_OFFLINE") and env.getArg("INSTALL_OFFLINE") == True
