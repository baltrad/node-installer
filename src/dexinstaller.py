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

DEX Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-11
'''
from installer import installer
import os, subprocess, shutil, errno
from osenv import osenv
from InstallerException import InstallerException

##
# The dex installer
#
class dexinstaller(installer):
  ##
  # Constructor
  # Installs the dex package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      #LD_LIBRARY_PATH=`generate_ld_path` 
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":""})
    super(dexinstaller, self).__init__(pkg, oenv)

  ##
  # Creates the directory including any parent directory
  # @param path: the directory to be created
  #
  def mkdir_recursive(self, path):
    try:
      os.makedirs(path)
    except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(path):
        pass
      else: 
        raise

  ##
  # Installs the javadoc documentation
  # @param env: the build environment
  #
  def _install_javadoc(self, env):
    pth = env.expandArgs("$PREFIX/doc/dex/doc/javadoc")
    if os.path.exists("doc/build/javadoc"):
      self.mkdir_recursive(pth)
      shutil.rmtree(pth, True)
      shutil.copytree("doc/build/javadoc", pth)

  ##
  # Installs the doxygen documentation
  # @param env: the build environment
  #
  def _install_doxygendoc(self, env):
    pth = env.expandArgs("$PREFIX/doc/dex/doc/doxygen")
    if os.path.exists("doc/build/doxygen"):
      self.mkdir_recursive(pth)
      shutil.rmtree(pth, True)
      shutil.copytree("doc/build/doxygen", pth)
    
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    cdir = self.package().fetch(env)
    
    os.chdir(cdir)

    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", env.getLdLibraryPath())
    
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -Dinstall.prefix=$PREFIX -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbeast.path=$PREFIX/beast -Djavahdf.path=$HDFJAVAHOME install"), shell=True)
    if ocode != 0:
      raise InstallerException("Failed to install dex")

    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -Dinstall.prefix=$PREFIX -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbeast.path=$PREFIX/beast -Djavahdf.path=$HDFJAVAHOME javadoc-doc > /dev/null 2>&1"), shell=True)
    if ocode != 0:
      print("Failed to generate javadoc for DEX")
    else:
      print("Installing javadoc")
      self._install_javadoc(env)
    
    ocode = subprocess.call(env.expandArgs("$TPREFIX/ant/bin/ant -Dinstall.prefix=$PREFIX -Dbaltrad.db.path=$PREFIX/baltrad-db -Dbeast.path=$PREFIX/beast -Djavahdf.path=$HDFJAVAHOME doxygen-doc > /dev/null 2>&1"), shell=True)
    if ocode != 0:
      print("Failed to generate DEX documentation")
    else:
      print("Installing doxygen documentation")
      self._install_doxygendoc(env)


    