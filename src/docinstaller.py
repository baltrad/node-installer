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
import os, subprocess, shutil
from osenv import osenv
from InstallerException import InstallerException

##
# The document installer. Will create a budle containing all documentation and
# place it in <prefix>/doc. Note, it should not be links to the existing documentation
# but instead the actual files.
#
class docinstaller(installer):
  ##
  # Constructor
  # Installs the dex package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"ANT_HOME":"$TPREFIX/ant",
                    "JAVA_HOME":"$JDKHOME",
                    "PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":""})
    super(docinstaller, self).__init__(pkg, oenv)
  
  ##
  # Returns all files that are in a directory. It will not
  # return directories or links.
  # @param dir: The directory name
  # @return: a list of files
  def _get_files_in_directory(self, dir):
    import glob
    result = []
    files = glob.glob("%s/*"%dir)
    
    for file in files:
      if os.path.isfile(file) and not os.path.islink(file):
        result.append(file)
    
    return result
    
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    import re
        
    hlhdf_pth = env.expandArgs("$PREFIX/doc/hlhdf")
    beast_pth = env.expandArgs("$PREFIX/doc/beast")
    dex_pth = env.expandArgs("$PREFIX/doc/dex")
    rave_pth = env.expandArgs("$PREFIX/doc/rave")
    bropo_pth = env.expandArgs("$PREFIX/doc/bropo")
    beamb_pth = env.expandArgs("$PREFIX/doc/beamb")
    
    pth = env.getInstallerPath() 
    os.chdir("%s/doxygen"%pth)
    
    if os.path.exists("doxygen"):
      shutil.rmtree("doxygen", True)
    if os.path.exists("baltrad.dox"):
      os.remove("baltrad.dox")
      
    shutil.copy("%s/doc/baltrad.dox"%pth, "./baltrad.dox")
    
    select_modules = "\n"
    if not env.isExcluded("HLHDF") and os.path.exists(hlhdf_pth):
      select_modules = select_modules + " - <a href=\"hlhdf/index.html\">HLHDF</a>\n"
    if not env.isExcluded("BEAST") and os.path.exists(beast_pth):
      select_modules = select_modules + " - <a href=\"beast/doc/doxygen/index.html\">BEAST Overview</a>\n"
      select_modules = select_modules + " - <a href=\"beast/doc/javadoc/index.html\">BEAST Java API</a>\n"
    if not env.isExcluded("BALTRAD-DEX") and os.path.exists(dex_pth):
      select_modules = select_modules + " - <a href=\"dex/index.html\">DEX (Data Exchange)</a>\n"
    if not env.isExcluded("RAVE") and os.path.exists(rave_pth):
      select_modules = select_modules + " - <a href=\"rave/index.html\">Radar Analysis and Visualization Environment (RAVE)</a>\n"
    if not env.isExcluded("BROPO") and os.path.exists(bropo_pth):
      select_modules = select_modules + " - <a href=\"bropo/index.html\">FMI Anomaly detection and removal package (ROPO)</a>\n"
    if not env.isExcluded("BEAMB") and os.path.exists(beamb_pth):
      select_modules = select_modules + " - <a href=\"beamb/index.html\">SMHI Beam blockage package (BEAMB)</a>\n"

    fp = open("%s/doc/baltrad.dox"%pth, "r")
    lines = fp.readlines()
    fp.close()
    
    fp = open("baltrad.dox", "w")
    for line in lines:
      line = re.sub("\\$REPLACE_MODULES_BY_DOCINSTALLER\\$",select_modules,line)
      fp.write(line)
    fp.close()

    ocode = subprocess.call("doxygen doxygen.cfg > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print "Failed to generate installation documentation"
      return

    pth = env.expandArgs("$PREFIX/doc")
    if os.path.exists("doxygen/html"):
      files_in_directory=self._get_files_in_directory(pth)
      for ft in files_in_directory:
        ftremove = "%s/%s"%(pth, ft)
        if os.path.exists(ftremove):
          os.remove(ftremove)

      files_to_copy = self._get_files_in_directory("doxygen/html")
      for ft in files_to_copy:
        shutil.copy(ft, "%s/"%pth)
      
    