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
import os, subprocess, glob, shutil
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
    bdbpython = env.expandArgs("${PREFIX}/baltrad-db/bin/python")

    # create a virtual python environment
    ocode = subprocess.call([
        python, "./misc/virtualenv/virtualenv.py",
         "--system-site-packages", "--distribute",
         env.expandArgs("${PREFIX}/baltrad-db")
    ])
    
    if ocode != 0:
      raise InstallerException, "Failed to create virtual environment"

    easyinstallstr = env.expandArgs("${PREFIX}/baltrad-db/bin/easy_install")
    if os.path.exists(easyinstallstr):
      # We always ends upp with a 0.6.24 version since the virtual env vill make sure of it. Upgrade it to later version
      ocode = subprocess.Popen(["%s --upgrade distribute"%easyinstallstr], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True).communicate()[0]
      #print "OCODE: %s"%ocode
      #ocode = subprocess.Popen(["%s --version"%easyinstallstr], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True).communicate()[0]
      #print "VERSION: %s"%ocode
    #print "OCODE=%s"%ocode
    #import sys
    #sys.exit(0)

    # First we remove old sins
    spth = subprocess.Popen(["%s -c %s"%(bdbpython, '"from distutils.sysconfig import get_python_lib; print(get_python_lib())"')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True).communicate()[0]
    spth = spth.strip()
    gstr = "%s/*.egg" % spth
    eggs = glob.glob(gstr)
    for egg in eggs:
      bname = os.path.basename(egg)
      if bname.startswith("baltrad.bdbcommon-"):
        shutil.rmtree("%s/%s"%(spth, bname))
      elif bname.startswith("baltrad.bdbclient-"):
        shutil.rmtree("%s/%s"%(spth, bname))
    
    self._install_and_test_python_package(
        "baltrad.bdbcommon",
        path=os.path.join(dir, "common"),
        python=python,
    )

    onlyclient=False
    if env.hasArg("SUBSYSTEMS") and len(env.getArg("SUBSYSTEMS")) > 0:
      if "RAVE" in env.getArg("SUBSYSTEMS") and "BDB" not in env.getArg("SUBSYSTEMS"):
        onlyclient = True
 
    # Install bdbserver in the virtual environment
    if onlyclient == False:
      self._install_and_test_python_package(
                                            "baltrad.bdbserver",
                                            path=os.path.join(dir, "server"),
                                            python=bdbpython,
                                            )
    
    self._install_and_test_python_package(
        "baltrad.bdbclient",
        path=os.path.join(dir, "client/python"),
        python=python,
    )
    
    if not os.path.exists(env.expandArgs("${PREFIX}/baltrad-db/bin/baltrad-bdb-client")):
      lncmd=env.expandArgs("ln -s ${TPREFIX}/bin/baltrad-bdb-client ${PREFIX}/baltrad-db/bin/baltrad-bdb-client")
      ocode = subprocess.call(lncmd, shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to create symbolic link for baltrad-bdb-client"

    ant = env.expandArgs("${TPREFIX}/ant/bin/ant")

    self._install_java_client(
        os.path.join(dir, "client/java"),
        prefix=env.expandArgs("${PREFIX}/baltrad-db"),
        ant=ant
    )

  def _install_and_test_python_package(self, name, path, python):
    os.chdir(path)

    ocode = subprocess.call([python, "setup.py", "install"])
    if ocode != 0:
        raise InstallerException, "Failed to install %s" % name
    
    ocode = subprocess.call(" ".join([
        python, "setup.py", "nosetests", "--first-package-wins", "-w test",
    ]), shell=True)
    if ocode != 0:
        raise InstallerException, "%s tests failed" % name
    
  def _install_java_client(self, path, prefix, ant):
    os.chdir(path)

    ocode = subprocess.call([ant, "-Dprefix=%s" % prefix, "test", "install"])
    if ocode != 0:
        raise InstallerException, "Failed to install BDB java client"
