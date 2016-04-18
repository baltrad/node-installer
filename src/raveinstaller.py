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

RAVE Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-11
'''
from installer import installer
import os, subprocess, shutil
from osenv import osenv
from InstallerException import InstallerException

##
# The RAVE installer
#
class raveinstaller(installer):
  ##
  # Constructor
  # Installs the RAVE package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$$PATH",
                    "LD_LIBRARY_PATH":"$$LD_LIBRARY_PATH",
                    "EXPATARG":"$TPREFIX",
                    "HLDIR":"$PREFIX/hlhdf",
                    "PROJ4ROOT":"$TPREFIX",
                    "PGF_PORT":"$RAVE_PGF_PORT",
                    "LOGPORT":"$RAVE_LOG_PORT",
                    "CENTER_ID":"$RAVE_CENTER_ID",
                    "DEX_SPOE":"$RAVE_DEX_SPOE",
                    "BUFRARG":"",
                    "DEX_PRIVATEKEY":"$PREFIX/etc/bltnode-keys/$NODENAME.priv",
                    "BDB_CONFIG_FILE":"$PREFIX/etc/bltnode.properties",
                    "DEX_NODENAME":"$NODENAME",
                    "RAVEROOT":"$PREFIX/rave"}, # RAVEROOT is the installation path....
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(raveinstaller, self).__init__(pkg, oenv)

  ##
  # Installs the documentation
  # @param env: the build environment
  def _install_doc(self, env):
    pth = env.expandArgs("$PREFIX/doc/rave")
    if os.path.exists("doxygen/doxygen/html"):
      if os.path.exists(pth):
        shutil.rmtree(pth, True)
      shutil.copytree("doxygen/doxygen/html", pth)

  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    
    if not env.isExcluded("BBUFR"):
      self.osenvironment().setEnvironmentVariable(env, "BUFRARG", "$PREFIX/bbufr")
    
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),self.osenvironment().getSnapshotVariable("LD_LIBRARY_PATH")))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),self.osenvironment().getSnapshotVariable("PATH")))

    ocode = subprocess.call("make distclean", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to perform distclean"

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to build"

    ocode = subprocess.call("make test", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to test"

    ocode = subprocess.call("make doc > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print "Failed to generate RAVE documentation"
    else:
      self._install_doc(env)

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install"
    
    self._update_pgf_registry(env)
    self._update_pgf_quality_registry(env)
    
  def _update_pgf_registry(self, env):
    if os.path.exists("tmpreg.py"):
      os.unlink("tmpreg.py")
    fp = open("tmpreg.py", "w")
    fp.write(env.expandArgs("""
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="$PREFIX/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatesite2d')
a.register('eu.baltrad.beast.generatesite2d', 'rave_pgf_site2D_plugin', 'generate', 'Generate Site2D plugin', 'area,quantity,method,date,time,anomaly-qc,prodpar,applygra,ignore-malfunc,ctfilter,pcsid,algorithm_id', '', 'height,range,zrA,zrb,xscale,yscale')
a.deregister('eu.baltrad.beast.generatecomposite')
a.register('eu.baltrad.beast.generatecomposite', 'rave_pgf_composite_plugin', 'generate', 'Generate composite plugin', 'area,quantity,method,date,time,selection,anomaly-qc,prodpar,applygra,ignore-malfunc,ctfilter,qitotal_field,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('eu.baltrad.beast.generatevolume')
a.register('eu.baltrad.beast.generatevolume', 'rave_pgf_volume_plugin', 'generate', 'Polar volume generation from individual scans', 'source,date,time,anomaly-qc,algorithm_id,merge', '', 'height,range,zrA,zrb')
a.deregister('se.smhi.rave.creategmapimage')
a.register('se.smhi.rave.creategmapimage', 'googlemap_pgf_plugin', 'generate', 'Google Map Plugin', 'outfile,date,time,algorithm_id', '', '')
a.deregister('eu.baltrad.beast.eu.baltrad.beast.applyqc')
a.register('eu.baltrad.beast.applyqc', 'rave_pgf_apply_qc_plugin', 'generate', 'Apply quality controls on a polar volume', 'date,time,anomaly-qc,algorithm_id', '', '')
"""))
    fp.close()


    try:    
      ocode = subprocess.call("python tmpreg.py", shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to register google maps plugin in rave"
    finally:
      if os.path.exists("tmpreg.py"):   
        os.unlink("tmpreg.py")    

  def _update_pgf_quality_registry(self, env):
    if os.path.exists("tmpreg.py"):
      os.unlink("tmpreg.py")
    fp = open("tmpreg.py", "w")
    fp.write(env.expandArgs("""
from rave_pgf_quality_registry_mgr import rave_pgf_quality_registry_mgr
a = rave_pgf_quality_registry_mgr("$PREFIX/rave/etc/rave_pgf_quality_registry.xml")
"""))
    fp.write(env.expandArgs("""
if not a.has_plugin("scansun"):
  a.add_plugin("scansun", "rave_scansun_quality_plugin", "scansun_quality_plugin")
  a.save("$PREFIX/rave/etc/rave_pgf_quality_registry.xml")  
"""))
    fp.close()
    
    try:    
      ocode = subprocess.call("python tmpreg.py", shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to register quality plugins in rave"
    finally:
      if os.path.exists("tmpreg.py"):   
        os.unlink("tmpreg.py")
