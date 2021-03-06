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

Fetcher class to combine with packages installed from PIP
'''
import os
import subprocess

from fetcher import fetcher
from InstallerException import InstallerException

##
# The url fetcher class
class pipfetcher(fetcher):
  ##
  # Constructor
  # @param url: the url to the file to be fetched
  #
  def __init__(self, pip_path="$TPREFIX/bin/pip", quiet=False):
    super(pipfetcher, self).__init__()
    self._pip_path = pip_path
    self._quiet = quiet
  
  ##
  # Fetches the file
  # @param package: the package to fetch
  # @param env: the build environment
  # @return the name of the file that was fetched
  #
  def dofetch(self, package, env=None):
    return ""

  ##
  # Fetches the file
  # @param package: the package to fetch
  # @param env: the build environment
  #  
  def dofetch_offline_content(self, package, env=None):
    pypi_name = _get_pypi_name(package)
    pip = env.expandArgs(self._pip_path)
    pkg_dir = os.path.join(
      env.getInstallerPath(),
      "packages",
      package.name(),
    )

    args = [pip, "install"]
    args.append("--build=%s" % pkg_dir)
    if self._quiet:
        args.append("--quiet")
    args.append("--no-install")
    args.append("--no-deps")
    args.append("--ignore-installed")
    args.append("%s == %s" % (pypi_name, package.version()))

    print(" ".join(args))
    ocode = subprocess.call(args)
    if ocode != 0:
      raise InstallerException(
        "Failed to fetch '%s' using pip" % pypi_name
      )

  ##
  # Removes the file
  # @param package: the package to clean
  # @param env: the build environment
  #
  def doclean(self, package, env=None):
    pass


def _get_pypi_name(pkg):
  if not hasattr(pkg, "pypi_name"):
      return pkg.name()
  else:
      return pkg.pypi_name
