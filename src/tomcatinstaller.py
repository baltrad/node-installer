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

Tomcat specific installer.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-04
'''
from installer import installer
from InstallerException import InstallerException
import subprocess
import shutil, os

##
# The tomcat installer
class tomcatinstaller(installer):
  ##
  # Constructor
  #
  def __init__(self, package):
    super(tomcatinstaller, self).__init__(package, None)
  
  ##
  # Performs the actual installation
  # @param env: the build environment
  #
  def doinstall(self, env):
    dir = self.package().fetch()

    if self.isTomcatRunning(env):
      raise InstallerException, "Tomcat process is running, please stop it first"

    shutil.rmtree(env.expandArgs("$TPREFIX/tomcat.bak"), True)
    if os.path.isdir(env.expandArgs("$TPREFIX/tomcat")):
      shutil.move(env.expandArgs("$TPREFIX/tomcat"), env.expandArgs("$TPREFIX/tomcat.bak"))
    
    shutil.move(dir, env.expandArgs("$TPREFIX/tomcat"))

    self.write_tomcat_users(env.expandArgs("$TPREFIX/tomcat"))
    
    self.write_root_index_file(env.expandArgs("$TPREFIX/tomcat"))
    
    self.patch_server_xml(dir, env.getArg("TOMCATPORT"), env.expandArgs("$TPREFIX/tomcat"), env.getInstallerPath())
  
  ##
  # Checks if tomcat already is running or not by using ps
  # @param env: the build environment
  # @return: True or False
  #
  def isTomcatRunning(self, env):
    result = False
    ps = subprocess.Popen(['ps', '-edalf'], stdout=subprocess.PIPE).communicate()[0]
    processes = ps.split('\n')
    for p in processes:
      if p.find("tomcat") >= 0:
        if p.find(env.expandArgs("$TPREFIX")) >= 0:
          result = True
    
    return result 
  
  ##
  # Creates the tomcat users file
  # @param troot: the tomcat root directory
  #
  def write_tomcat_users(self, troot):
    filename = "%s/conf/tomcat-users.xml"%troot
    fp = open(filename, "w")
    fp.write("""<?xml version='1.0' encoding='utf-8'?>
<tomcat-users>
  <role rolename="manager"/>
  <role rolename="tomcat"/>
  <role rolename="admin"/>
  <user username="admin" password="secret" roles="admin,tomcat,manager"/>
</tomcat-users>
    """)
    fp.close()
  
  ##
  # Writes the index.html file
  # @param troot: the tomcat root directory
  #
  def write_root_index_file(self, troot):
    filename = "%s/webapps/ROOT/index.html"%troot
    fp = open(filename, "w")
    fp.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML>
  <HEAD>
    <TITLE></TITLE>
    <META http-equiv="refresh" content="0;URL=/BaltradDex">
  </HEAD>
  <BODY>
  </BODY>
</HTML>
    """)
    fp.close()
  
  ##
  # Installs a patched version of server.xml
  # @param patchdir: the name of the directory where the patch file resides. Path will be thisdir/../patches/<patchdir>/server.xml.in
  # @param portstr: The port the tomcat server should listen on
  # @param troot: tomcat root directory
  #
  def patch_server_xml(self, patchdir, portstr, troot, installerroot):
    ifp = open("%s/patches/%s/server.xml.in"%(installerroot, patchdir), "r")
    ofp = open("%s/conf/server.xml"%troot, "w")
    inlines = ifp.readlines()
    for l in inlines:
      tl = l
      if tl.find("CFG_TOMCATPORT") >= 0:
        tl = tl.replace("CFG_TOMCATPORT", portstr)
      ofp.write(tl)
    ifp.close()
    ofp.close()
