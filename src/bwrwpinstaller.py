'''
Copyright (C) 2013 Swedish Meteorological and Hydrological Institute, SMHI,

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

BWRWP Installer

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2013-09-25
'''
from installer import installer
import os, subprocess, string
from osenv import osenv
from InstallerException import InstallerException

##
# The BWRWP installer
#
class bwrwpinstaller(installer):
  ##
  # Constructor
  # Installs the bbufr package. 
  #
  def __init__(self, pkg, oenv = None):
    if oenv == None:
      oenv = osenv({"PATH":"$TPREFIX/bin:$$PATH",
                    "LD_LIBRARY_PATH":"$TPREFIX/lib:$$LD_LIBRARY_PATH",
                    "EXPATARG":"$TPREFIX",
                    "HLDIR":"$PREFIX/hlhdf",
                    "PROJ4ROOT":"$TPREFIX",
                    "RAVEROOT":"$PREFIX/rave"}, # RAVEROOT is the installation path....
                    defaultosenv={"LD_LIBRARY_PATH":""})
    super(bwrwpinstaller, self).__init__(pkg, oenv)
  
  ##
  # Returns the zlib arguments
  # @param benv: the build environment
  def get_zlib_args(self, benv):
    inc = None
    lib = None
    if benv.hasArg("ZLIBINC"):
      inc = benv.getArg("ZLIBINC")
    if benv.hasArg("ZLIBLIB"):
      lib = benv.getArg("ZLIBLIB")

    if inc != None and inc != "":
      inc = "-I%s"%inc
    if lib != None and lib != "":
      lib = "-L%s"%lib
    
    return (inc, lib)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch(env)
    
    os.chdir(dir)
    self.osenvironment().setEnvironmentVariable(env, "LD_LIBRARY_PATH", "%s:%s"%(env.getLdLibraryPath(),self.osenvironment().getSnapshotVariable("LD_LIBRARY_PATH")))
    self.osenvironment().setEnvironmentVariable(env, "PATH", "%s:%s"%(env.getPath(),self.osenvironment().getSnapshotVariable("PATH")))
    
    #  $ ./configure --with-rave=/opt/baltrad/rave --with-blas=/projects/baltrad/SMHI_WRWP/BLAS -
    #     -with-cblas=/projects/baltrad/SMHI_WRWP/CBLAS --with-lapack=/projects/baltrad/SMHI_WRWP/lapa
    #      ck-3.4.2 --with-lapacke=/projects/baltrad/SMHI_WRWP/lapack-3.4.2/lapacke/include,/projects/b
    #      altrad/SMHI_WRWP/lapack-3.4.2
    
    # Dont check error code for distclean, it will fail if fresh build
    # so we wait with failing until next call is performed
    subprocess.call("make distclean", shell=True)

    cmd = "./configure --prefix=\"$PREFIX/baltrad-wrwp\" --with-rave=\"$PREFIX/rave\"" # --with-blas=\"$BLASARG\""
    if env.hasArg("BLASARG"):
      cmd = "%s --with-blas=\"$BLASARG\""%cmd
    if env.hasArg("CBLASARG"):
      cmd = "%s --with-cblas=\"$CBLASARG\""%cmd
    if env.hasArg("LAPACKARG"):
      cmd = "%s --with-lapack=\"$LAPACKARG\""%cmd
    if env.hasArg("LAPACKEARG"):
      cmd = "%s --with-lapacke=\"$LAPACKEARG\""%cmd
      
    newcmd = env.expandArgs(cmd)
    
    #print "NEWCMD: %s"%newcmd
    #exit(255)
    ocode = subprocess.call(newcmd, shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to configure baltrad-wrwp"

    ocode = subprocess.call("make", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to build baltrad-wrwp"

    ocode = subprocess.call("make test", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to test baltrad-wrwp"      

    ocode = subprocess.call("make doc > /dev/null 2>&1", shell=True)
    if ocode != 0:
      print "Failed to generate baltrad-wrwp documentation"
    else:
      self._install_doc(env)

    ocode = subprocess.call("make install", shell=True)
    if ocode != 0:
      raise InstallerException, "Failed to install baltrad-wrwp"
    
    cmd = "python -c \"import sys;import os;print os.sep.join([sys.prefix, 'lib', 'python'+sys.version[:3],'site-packages'])\""
    plc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).communicate()[0]
    foutname = "%s/baltrad-wrwp.pth"%string.strip(plc)

    try:
      fp = open(foutname, "w")
      fp.write(env.expandArgs("$PREFIX/baltrad-wrwp/share/wrwp/pywrwp"))
      fp.close()
    except Exception, e:
      raise InstallerException, "Failed to generate baltrad-wrwp.pth in python site-packages, %s"%`e.__str__()`

    self._configure_rave_plugin(env)
  
  def _configure_rave_plugin(self, env):
    env.getNodeScript().stop(rave=True)
    
    if os.path.exists("tmpreg.py"):
      os.unlink("tmpreg.py")
    fp = open("tmpreg.py", "w")
    fp.write(env.expandArgs("""
from rave_pgf_registry import PGF_Registry
a=PGF_Registry(filename="$PREFIX/rave/etc/rave_pgf_registry.xml")
a.deregister('eu.baltrad.beast.generatewrwp')
a.deregister('se.smhi.baltrad-wrwp.generatewrwp')
a.register('eu.baltrad.beast.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', '','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
a.register('se.smhi.baltrad-wrwp.generatewrwp', 'baltrad_wrwp_pgf_plugin', 'generate', 'Baltrad WRWP Plugin', '','interval,maxheight,mindistance,maxdistance','minelevationangle,velocitythreshold')
"""))
    fp.close()

    try:    
      ocode = subprocess.call("python tmpreg.py", shell=True)
      if ocode != 0:
        raise InstallerException, "Failed to register google maps plugin in rave"
    finally:
      if os.path.exists("tmpreg.py"):   
        os.unlink("tmpreg.py")

    