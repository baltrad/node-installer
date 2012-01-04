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

Baltrad DB Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-09
'''
from installer import installer
import os, subprocess
from osenv import osenv
from InstallerException import InstallerException

##
# The Baltrad DB installer
#
class bdbinstaller(installer):
  ##
  # Constructor
  # Installs the baltrad db package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME", 
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$PREFIX/hlhdf/lib:$$LD_LIBRARY_PATH"},
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(bdbinstaller, self).__init__(pkg, oenv)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = os.path.abspath(self.package().fetch(env))

    os.chdir(dir)

    python = env.expandArgs("$TPREFIX/bin/python")
    
    # create a virtual python environment
    ocode = subprocess.call([
        python, "./misc/virtualenv/virtualenv.py",
         "--system-site-packages", "--distribute",
         env.expandArgs("${PREFIX}/baltrad-db")
    ])

    if ocode != 0:
      raise InstallerException, "Failed to create virtual environment"

    pip = env.expandArgs("${PREFIX}/baltrad-db/bin/pip")
    python = env.expandArgs("${PREFIX}/baltrad-db/bin/python")
    
    # we are going to run tests post-install, so add nose and mock to the env
    self._pip_install(pip, "nose >= 1.1")
    self._pip_install(pip, "mock >= 0.7")

    self._install_and_test_python_package(
        "baltrad.bdbcommon",
        path=os.path.join(dir, "common"),
        python=python,
    )

    self._install_and_test_python_package(
        "baltrad.bdbserver",
        path=os.path.join(dir, "server"),
        python=python,
    )

    self._install_and_test_python_package(
        "baltrad.bdbclient",
        path=os.path.join(dir, "client/python"),
        python=python,
    )

    ant = env.expandArgs("${TPREFIX}/ant/bin/ant")

    self._install_java_client(
        os.path.join(dir, "client/java"),
        prefix=env.expandArgs("${PREFIX}/baltrad-db"),
        ant=ant
    )

  def _install_and_test_python_package(self, name, path, python):
    os.chdir(path)

    ocode = subprocess.call([python, "setup.py", "--quiet", "install"])
    if ocode != 0:
        raise InstallerException, "Failed to install %s" % name
    
    ocode = subprocess.call([
        python, "setup.py", "nosetests",
        "--first-package-wins",
        "-A 'not dbtest'",
    ])
    if ocode != 0:
        raise InstallerException, "%s tests failed" % name
    
  def _pip_install(self, pip, package):
    ocode = subprocess.call([pip, "install", "%s" % package])
    if ocode != 0:
        raise InstallerException, "Failed to pip-install '%s'" % package
  
  def _install_java_client(self, path, prefix, ant):
    os.chdir(path)

    ocode = subprocess.call([ant, "-Dprefix=%s" % prefix, "test", "install"])
    if ocode != 0:
        raise InstallerException, "Failed to install BDB java client"
