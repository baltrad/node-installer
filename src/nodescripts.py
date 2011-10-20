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

Wrapper for all node scripts

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-14
'''
import subprocess
import tempfile
import os, stat

##
# The node script wrapper
class nodescripts(object):
  _nodescript = None
  _initdscript = None
  _raveinitdscript = None
  _rcsource = None
  _path = None
  _ldlibrarypath = None
  _version = "0.0.0"
  _raveinstalled = False
  
  ##
  # Constructor
  #  
  def __init__(self, path, ldlibrarypath, version, raveinstalled=False):
    self._path = path
    self._ldlibrarypath = ldlibrarypath
    self._version = version
    self._nodescript = None
    self._initdscript = None
    self._raveinitdscript = None
    self._rcsource = None
    self._raveinstalled = raveinstalled
  
  ##
  # Creates the scripts
  #
  def create_scripts(self, env):
    self._nodescript = self._create_bltnode_script(env)
    self._initdscript = self._create_initd_script(env)
    self._rcsource = self._create_bltnoderc_script(env)
    self._raveinitdscript = self._create_rave_initd_script(env)

  ##
  # Creates the blt node script
  # @param env: the build environment
  #
  def _create_bltnode_script(self, env):
    extras = {}
    extras["BALTRAD_NODE_VERSION"] = self._version
    #print "LDLIBRARYPATH: %s"%self._ldlibrarypath
    extras["LIBPATH"] = env.expandArgs("%s"%self._ldlibrarypath)
    extras["PPATH"] = env.expandArgs("%s"%self._path)
    if self._raveinstalled:
      extras["INSRAVE"] = "yes"
    else:
      extras["INSRAVE"] = "no"
    fpd, filename = tempfile.mkstemp(suffix=".tmp", prefix="bltnode")

    ofp = os.fdopen(fpd, "w")
    ofp.write(env.expandArgs("""
#!/bin/sh
# Autogenerated by baltrad-core/setup
# Version: ${BALTRAD_NODE_VERSION}
# Prefix: $PREFIX
# DepPrefix: $TPREFIX

export LD_LIBRARY_PATH="$LIBPATH"
PATH="$PPATH"
export JAVA_HOME="$JDKHOME"
export CATALINA_HOME="$TPREFIX/tomcat"
export RAVEPGF_SUPPORT="$INSRAVE"

check_status() {
  ENTRIES=`ps -edalf | grep tomcat | grep "baltrad.node.startup.indicator" | sed -e"s/.*-Dbaltrad.node.startup.indicator=\\"\\([^\\"]*\\)\\".*/\\1/g"`
  for item in $$ENTRIES; do
    if [ "$$item" = "$$CATALINA_HOME" ]; then
      return 0
    fi
  done
  return 1
}

start() {
  echo -n "Starting baltrad-node..."
  check_status
  if [ $$? -eq 0 ]; then
    echo " already running..."
  else
    "$${CATALINA_HOME}/bin/startup.sh" -Dbaltrad.node.startup.indicator=\\"$${CATALINA_HOME}\\"
  fi
}

stop() {
  echo "Stopping baltrad-node..."
  "$${CATALINA_HOME}/bin/shutdown.sh"
}

status() {
  check_status
  if [ $$? -eq 0 ]; then
    echo "Running"
  else
    echo "Stopped"
  fi
}

check_ravepgf_status() {
  RAVEPGFPROCESS=`$PREFIX/rave/bin/rave_pgf status`
  if [ "$$RAVEPGFPROCESS" = "rave_pgf is not running" ]; then
    return 1
  fi
  return 0
}

start_ravepgf() {
  echo -n "Starting rave-pgf..."
  check_ravepgf_status
  if [ $$? -eq 0 ]; then
    echo " already running..."
  else
    "$PREFIX/rave/bin/rave_pgf" start
    echo ""
  fi
}

stop_ravepgf() {
  echo "Stopping rave-pgf..."
  "$PREFIX/rave/bin/rave_pgf" stop
}

status_ravepgf() {
  check_ravepgf_status
  if [ $$? -eq 0 ]; then
    echo "Running"
  else
    echo "Stopped"
  fi
}

print_usage() {
  echo "Usage: $$0 [options] {start|stop|status}"
  echo "Options: --ravepgf  - only affect ravepgf"
  echo "         --all      - affect all processes"
  echo "No options will result in only the node server to be managed"
}

START_REQUEST=no
STOP_REQUEST=no
STATUS_REQUEST=no
RAVEPGF_REQUEST=no
ALL_REQUEST=no

# See how we were called.
for arg in $$*; do
  case $$arg in
    start)
      START_REQUEST=yes
      ;;
    stop)
      STOP_REQUEST=yes
      ;;
    status)
      STATUS_REQUEST=yes
      ;;
    --ravepgf)
      RAVEPGF_REQUEST=yes
      ;;
    --all)
      ALL_REQUEST=yes
      ;;
    *)
      print_usage
      exit 1
  esac
done

if [ "$${RAVEPGF_SUPPORT}" = "no" -a "$${RAVEPGF_REQUEST}" = "yes" ]; then
  echo "RavePGF support has not been enabled during installation!"
  exit 1;
fi

if [ "$${START_REQUEST}" = "yes" ]; then
  if [ "$${RAVEPGF_REQUEST}" = "yes" ]; then
    start_ravepgf
  elif [ "$${ALL_REQUEST}" = "yes" ]; then
    if [ "$${RAVEPGF_SUPPORT}" = "yes" ]; then
      start_ravepgf
    fi
    start
  else
    start
  fi
elif [ "$${STOP_REQUEST}" = "yes" ]; then
  if [ "$${RAVEPGF_REQUEST}" = "yes" ]; then
    stop_ravepgf
  elif [ "$${ALL_REQUEST}" = "yes" ]; then
    stop
    if [ "$${RAVEPGF_SUPPORT}" = "yes" ]; then
      stop_ravepgf
    fi
  else
    stop
  fi
elif [ "$${STATUS_REQUEST}" = "yes" ]; then
  if [ "$${RAVEPGF_REQUEST}" = "yes" ]; then
    echo -n "Rave PGF: "
    status_ravepgf
  elif [ "$${ALL_REQUEST}" = "yes" ]; then
    echo -n "Node: "
    status
    if [ "$${RAVEPGF_SUPPORT}" = "yes" ]; then
      echo -n "Rave PGF: "
      status_ravepgf
    fi
  else
    echo -n "Node: "
    status
  fi
else
  print_usage
fi

""", extras))
    ofp.close()
    os.chmod(filename, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    return filename

  ##
  # @return: the temporary bltnode script file
  #
  def get_bltnode_script_path(self):
    return self._nodescript

  ##
  # Creates the init.d script
  # @param env: the build environment
  def _create_initd_script(self, env):
    fpd, filename = tempfile.mkstemp(suffix=".tmp", prefix="bltnode.init.d")
    ofp = os.fdopen(fpd, "w")
    ofp.write(env.expandArgs("""
#!/bin/sh
# Autogenerated by baltrad-core/setup
NODEUSER=$RUNASUSER

start() {
  su - $$NODEUSER -c "$PREFIX/bin/bltnode start"
}

stop() {
  su - $$NODEUSER -c "$PREFIX/bin/bltnode stop"
}

# See how we were called.
case "$$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  *)
    echo "Usage: $$0 {start|stop}"
    exit 1
esac
"""))
    ofp.close()
    os.chmod(filename, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    return filename

  ##
  # @return: the temporary init.d script file name
  #
  def get_initd_script_path(self):
    return self._initdscript

  ##
  # Creates the temporary rave init.d script file
  # @param env: the build environment
  #
  def _create_rave_initd_script(self, env):
    fpd, filename = tempfile.mkstemp(suffix=".tmp", prefix="ravepgf.init.d")
    ofp = os.fdopen(fpd, "w")
    ofp.write(env.expandArgs("""
#!/bin/sh
# Autogenerated by baltrad-core/setup
NODEUSER=$RUNASUSER

start() {
  su - $$NODEUSER -c "$PREFIX/bin/bltnode --ravepgf start"
}

stop() {
  su - $$NODEUSER -c "$PREFIX/bin/bltnode --ravepgf stop"
}

# See how we were called.
case "$$1" in
  start)
    start
    ;;
  stop)
    stop
    ;;
  *)
    echo "Usage: $$0 {start|stop}"
    exit 1
esac
"""))
    ofp.close()
    os.chmod(filename, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    return filename
  
  ##
  # @return: the temporary rave init.d script file name
  #
  def get_rave_initd_script_path(self):
    return self._raveinitdscript
  
  ##
  # Generates the resource file.
  # @param env: the build environment
  #
  def _create_bltnoderc_script(self, env):
    extras = {}
    extras["BALTRAD_NODE_VERSION"] = self._version
    extras["LIBPATH"] = env.expandArgs("$PREFIX/rave/lib:%s"%env.getLdLibraryPath())
    extras["PPATH"] = env.expandArgs("$PREFIX/rave/bin:%s"%env.getPath())
    if self._raveinstalled:
      extras["INSRAVE"] = "yes"
    else:
      extras["INSRAVE"] = "no"
    
    fpd, filename = tempfile.mkstemp(suffix=".tmp", prefix="bltnode.rc")
    ofp = os.fdopen(fpd, "w")
    ofp.write(env.expandArgs("""
# Autogenerated by baltrad-core/setup
# Version: ${BALTRAD_NODE_VERSION}
# Prefix: $PREFIX
# DepPrefix: $TPREFIX

if [ "$${LD_LIBRARY_PATH}" != "" ]; then
  export LD_LIBRARY_PATH="$LIBPATH:$${LD_LIBRARY_PATH}"
else
  export LD_LIBRARY_PATH="$LIBPATH"
fi
export JAVA_HOME="${JDKHOME}"
export CATALINA_HOME="$TPREFIX/tomcat"
if [ "$${PATH}" != "" ]; then
  export PATH="$PPATH:$${PATH}"
else
  export PATH="$PPATH"
fi

""", extras))
    ofp.close()
    os.chmod(filename, stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH)
    return filename

  ##
  # @return: the temporary resource file path name
  #
  def get_node_source_path(self):
    return self._rcsource

  ##
  # Uses the script to identify if the node (tomcat) is running
  # @return: True if it is running, otherwise False
  #
  def _isNodeRunning(self):
    status = subprocess.Popen("%s status"%self._nodescript, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True).communicate()[0]
    if status.find("Node: Running") >= 0:
      return True
    return False

  ##
  # Uses the script to identify if the rave pgf is running
  # @return: True if it is running, otherwise False
  # 
  def _isRaveRunning(self):
    status = subprocess.Popen("%s --ravepgf status"%self._nodescript, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True).communicate()[0]
    if status.find("Rave PGF: Running") >= 0:
      return True
    return False 

  ##
  # Waits for the node to stop. A stop request should have been issued
  # prior to this method is called.
  # @param msg: A message to show that it is waiting
  # @param sec: how many seconds to wait
  # 
  # @return: True if the node has been stopped, otherwise False
  #   
  def _waitForNodeStop(self, msg, sec):
    import time, sys
    
    print msg
    
    for i in range(sec):
      if self._isNodeRunning():
        print ".",
        sys.stdout.flush()
        time.sleep(1)
      else:
        print ""
        return True
    print ""
    return False

  ##
  # Waits for the rave pgf to stop. A stop request should have been issued
  # prior to this method is called.
  # @param msg: A message to show that it is waiting
  # @param sec: how many seconds to wait
  # 
  # @return: True if the rave pgf has been stopped, otherwise False
  #  
  def _waitForRaveStop(self, msg, sec):
    import time, sys
    
    print msg
    
    for i in range(sec):
      if self._isRaveRunning():
        print ".",
        sys.stdout.flush()
        time.sleep(1)
      else:
        print ""
        return True
    print ""
    return False
  
  ##
  # Starts the requested functions.
  # @param node: if node should be started
  # @param rave: if rave pgf should be started
  #
  def start(self, node=False, rave=False):
    import time

    if node and not self._isNodeRunning():
      ocode = subprocess.call("%s start"%(self._nodescript), shell=True)
      if ocode != 0:
        raise Exception, "Failed to start node"
      time.sleep(2)    

    if rave and self._raveinstalled and not self._isRaveRunning():
      ocode = subprocess.call("%s --ravepgf start"%(self._nodescript), shell=True)
      if ocode != 0:
        raise Exception, "Failed to start rave"

  ##
  # Stops the requested functions.
  # @param node: if node should be stopped
  # @param rave: if rave pgf should be stopped
  #  
  def stop(self, node=False, rave=False):
    if node and self._isNodeRunning():
      ocode = subprocess.call("%s stop"%(self._nodescript),shell=True)
      if ocode != 0:
        raise Exception, "Failed to stop node"
    
      if not self._waitForNodeStop("Waiting for node to stop", 10):
        raise Exception, "Failed to stop node"
  
    if rave and self._raveinstalled and self._isRaveRunning():
      ocode = subprocess.call("%s --ravepgf stop"%(self._nodescript),shell=True)
      if ocode != 0:
        raise Exception, "Failed to stop rave"
    
      if not self._waitForRaveStop("Waiting for rave to stop", 10):
        raise Exception, "Failed to stop rave"
      
  ##
  # Restarts the requested functions.
  # @param node: if node should be restarted
  # @param rave: if rave pgf should be restarted
  #  
  def restart(self, node=False, rave=False):
    self.stop(node, rave)
    self.start(node, rave)
  
