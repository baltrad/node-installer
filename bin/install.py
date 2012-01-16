'''
Created on Jan 21, 2011

@author: anders
'''
import os
import getopt
import sys

sys.path.append("../src")
sys.path.append("../bin") # To get this directory

from InstallerException import InstallerException
from package import package
from urlfetcher import urlfetcher
from cmmi import cmmi
from untar import untar
from nodir import nodir
from buildenv import buildenv
from osenv import osenv
from shinstaller import shinstaller
from pilinstaller import pilinstaller
from tomcatinstaller import tomcatinstaller
from hdfjavainstaller import hdfjavainstaller
from hdfjavainstaller import hdfjavasetupinstaller
from machinefetcher import machinefetcher
from jdkvalidator import jdkvalidator
from zlibvalidator import zlibvalidator
from psqlvalidator import psqlvalidator
from doxygenvalidator import doxygenvalidator
from hlhdfinstaller import hlhdfinstaller
from bbufrinstaller import bbufrinstaller
from bdbinstaller import bdbinstaller
from beastinstaller import beastinstaller
from dexinstaller import dexinstaller
from raveinstaller import raveinstaller
from ravegmapinstaller import ravegmapinstaller
from bropoinstaller import bropoinstaller
from beambinstaller import beambinstaller
from dbinstaller import dbinstaller, dbupgrader
from nodescripts import nodescripts
from deployer import deployer
from configinstaller import configinstaller
from raveconfiginstaller import raveconfiginstaller
from scriptinstaller import scriptinstaller
from patcher import patcher
from finished import finished
from pipinstaller import pipinstaller
from pipfetcher import pipfetcher
from prepareinstaller import prepareinstaller
from keystoreinstaller import keystoreinstaller
from docinstaller import docinstaller

from node_package import node_package

from extra_functions import *
from node_installer import node_installer
from experimental import experimental

##
# All modules that should be installed for the baltrad node
# Note, it is essential that the order is correct here since
# they will be installed in this order. There is no dependency
# checking for this.
#
# So, if for example HDF5 is dependent on ZLIB. ZLIB must be installed prior to
# HDF5. But since HDF5 is dependent on ZLIB, HDF5 must get the depends set to ZLIB
# so that HDF5 is rebuilt each time ZLIB is rebuilt.
##
MODULES=[prepareinstaller(package("PREPARE", "1.0", nodir(), remembered=False)),
         shinstaller(package("ZLIB", "1.2.4", nodir()),":"),

         cmmi(package("HDF5", "1.8.5-patch1",
                      untar(urlfetcher("hdf5-1.8.5-patch1.tar.gz"), "hdf5-1.8.5-patch1", True),
                      depends=["ZLIB"]),
              "--prefix=\"$TPREFIX\" --with-pthread=yes --enable-threadsafe", False, True,
              foptionalarg=hdf5_optional_zlib_arg),
              
         cmmi(package("EXPAT", "2.0.1",
                      untar(urlfetcher("expat-2.0.1.tar.gz"), "expat-2.0.1", True)),
              "--prefix=\"$TPREFIX\"", False, True),
              
         cmmi(package("PROJ.4", "4.7.0",
                      untar(urlfetcher("proj-4.7.0.tar.gz"), "proj-4.7.0", True)),
              "--prefix=\"$TPREFIX\" --with-jni=\"$JDKHOME/include\"", False, True,
              osenv({"CFLAGS":"-I\"$JDKHOME/include/linux\""})),

         shinstaller(package("PYTHON", ".".join([str(x) for x in sys.version_info[:3]]), nodir()),
                     ":"),

         experimental(
           pipinstaller(
             package("NUMPY", "1.3.0",
               fetcher=pipfetcher(),
               depends=["PYTHON"],
             ),
             pypi_name="numpy",
           ),
           pipinstaller(
             package("NUMPY", "1.4.1",
               fetcher=pipfetcher(),
               depends=["PYTHON"],
             ),
             pypi_name="numpy",
           )
         ),

         pilinstaller(package("PIL", "1.1.7",
                              untar(urlfetcher("Imaging-1.1.7.tar.gz"), "Imaging-1.1.7", True),
                              depends=["PYTHON","ZLIB"])),
        
         experimental(
           cmmi(package("CURL", "7.19.0",
                        untar(urlfetcher("curl-7.19.0.tar.gz"), "curl-7.19.0", True)),
                "--prefix=\"$TPREFIX\"", False, True),
                      
           cmmi(package("CURL", "7.22.0",
                        untar(urlfetcher("curl-7.22.0.tar.gz"), "curl-7.22.0", True)),
                "--prefix=\"$TPREFIX\"", False, True)
         ),
              
         shinstaller(package("PYCURL", "7.19.0",
                             untar(urlfetcher("pycurl-7.19.0.tar.gz"), "pycurl-7.19.0", True),
                             depends=["PYTHON","CURL"]),
                     "\"$TPREFIX/bin/python\" setup.py install",
                     osenv({"LD_LIBRARY_PATH":"$TPREFIX/lib", "PATH":"$TPREFIX/bin:$$PATH"})),
]

_PIP_MODULES=[
    ("PYCRYPTO", "2.4.1", "pycrypto", ["PYTHON"]),
    ("PYASN1", "0.1.2", "pyasn1", ["PYTHON"]),
    ("PYTHON-KEYCZAR", "0.7b", "python-keyczar", ["PYTHON", "PYASN1", "PYCRYPTO"]),
    ("JPROPS", "0.1", "jprops", ["PYTHON"]),
    ("PYTHON-DAEMON", "1.6", "python-daemon", ["PYTHON"]),
    ("PSYCOPG2", "2.2.1", "psycopg2", ["PYTHON"]),
    ("SQLALCHEMY", "0.7.4", "sqlalchemy", ["PYTHON"]),
    ("WERKZEUG", "0.8.2", "werkzeug", ["PYTHON"]),
    ("PYTHON-MOCK", "0.7.2", "mock", ["PYTHON"]),
    ("NOSE", "1.1.2", "nose", ["PYTHON"]),
]

for (name, version, pypi_name, deps) in _PIP_MODULES:
    MODULES.append(
        pipinstaller(
            package(name, version, fetcher=pipfetcher(), depends=deps),
                    pypi_name=pypi_name))

MODULES.extend([
         tomcatinstaller(package("TOMCAT", "6.0.33",
                                 untar(urlfetcher("apache-tomcat-6.0.33.tar.gz"), "apache-tomcat-6.0.33", True))),
         
         hdfjavainstaller(package("HDFJAVA", "2.6.1",
                                  machinefetcher({
                                    'i386':untar(urlfetcher("hdf-java-2.6.1-i386-bin.tar"), "hdf-java", False),
                                    'x86_64':untar(urlfetcher("hdf-java-2.6.1-x86_64-bin.tar"), "hdf-java", False)}
                                  ))),
         
         shinstaller(package("ANT", "1.8.0",
                             untar(urlfetcher("apache-ant-1.8.0-bin.tar.gz"), ".", True)),
                     "rm -fr \"$TPREFIX/ant\"; mv -f apache-ant-1.8.0 \"$TPREFIX/ant\""),
                                   
         hdfjavasetupinstaller(package("HDFJAVASETUP", "2.6.1", depends=["TOMCAT", "HDFJAVA"])),
         
         # Time to install baltrad node software
         keystoreinstaller(package("KEYSTORE", "1.0", nodir())),
         
         hlhdfinstaller(node_package("HLHDF", depends=["ZLIB", "HDF5"])),

         bbufrinstaller(node_package("BBUFR", depends=["ZLIB"])),

         bdbinstaller(node_package("BALTRAD-DB", depends=["ZLIB", "HDF5", "HLHDF", "PQXX"])),
         
         beastinstaller(node_package("BEAST", depends=["BALTRAD-DB"])),
         
         dexinstaller(node_package("BALTRAD-DEX", depends=["HDFJAVA", "TOMCAT", "BALTRAD-DB", "BEAST"])),
         
         raveinstaller(node_package("RAVE", depends=["EXPAT", "PROJ.4", "PYTHON", "NUMPY", "PYSETUPTOOLS", "PYCURL", "HLHDF", "BBUFR"])),
         
         ravegmapinstaller(node_package("RAVE-GMAP", depends=["RAVE"])), #Just use rave as dependency, rest of dependencies will trigger rave rebuild

         bropoinstaller(node_package("BROPO", depends=["RAVE"])), #Just use rave as dependency, rest of dependencies will trigger rave rebuild

         beambinstaller(node_package("BEAMB", depends=["RAVE"])), #Just use rave as dependency, rest of dependencies will trigger rave rebuild

         docinstaller(package("DOCS", "1.0", nodir(), remembered=False)),
         
         configinstaller(package("CONFIG", "1.0", nodir(), remembered=False)),
         
         raveconfiginstaller(package("RAVECONFIG", "1.0", nodir(), remembered=False)),
         
         dbinstaller(package("DBINSTALL", "1.0", nodir())),
         
         dbupgrader(package("DBUPGRADE", "1.0", nodir(), remembered=False)),

         deployer(package("DEPLOY", "1.0", nodir(), depends=["BALTRAD-DEX"], remembered=False)),

         scriptinstaller(package("SCRIPT", "1.0", nodir(), remembered=False)),
         
         # Always keep this installer at the end. It will start the system
         # and print out relevant information.
         finished(package("FINISHED", "1.0", nodir(), remembered=False)),
        ])

##
# Prints the modules and the current version they have.
#
def print_modules(env):
  for module in MODULES:
    installed = "NOT INSTALLED"
    ver = env.getInstalled(module.package().name())
    if ver != None:
      installed = "INSTALLED"
    else:
      ver = module.package().version()
    print "{0:20s} {1:35s} {2:14s}".format(module.package().name(),ver, installed)

##
# Prints the current configuration
#
def print_arguments(env):
  arguments = [("--prefix=", env.getArg("PREFIX")),
               ("--tprefix=", env.getArg("TPREFIX")),
               ("--urlrepo=", env.getArg("URLREPO")),
               ("--dbuser=", env.getArg("DBUSER")),
               ("--dbname=", env.getArg("DBNAME")),
               ("--dbhost=", env.getArg("DBHOST")),
               ("--runas=", env.getArg("RUNASUSER")),
               ("--with-hdfjava=", env.getArg("HDFJAVAHOME")),
               ("--nodename=", env.getArg("NODENAME"))]
  
  if env.hasArg("ZLIBARG"):
    arguments.append(("--with-zlib=", env.getArg("ZLIBARG")))
  if env.hasArg("PSQLARG"):
    arguments.append(("--with-psql=", env.getArg("PSQLARG")))
  if env.hasArg("DATADIR"):
    arguments.append(("--datadir=", env.getArg("DATADIR")))
  if env.hasArg("TOMCATPORT"):
    arguments.append(("--tomcatport=", env.getArg("TOMCATPORT")))
  if env.hasArg("TOMCATURL"):
    arguments.append(("--tomcaturl=", env.getArg("TOMCATURL")))
  if env.hasArg("BUILD_BDBFS") and env.getArg("BUILD_BDBFS") == "yes":
    arguments.append(("--with-bdbfs", ""))
  if env.hasArg("WITH_RAVE") and env.getArg("WITH_RAVE") == True:
    arguments.append(("--with-rave", ""))
  if env.hasArg("WITH_RAVE_GMAP") and env.getArg("WITH_RAVE_GMAP") == True:
    arguments.append(("--with-rave-gmap", ""))
  if env.hasArg("WITH_BROPO") and env.getArg("WITH_BROPO") == True:
    arguments.append(("--with-bropo", ""))
  if env.hasArg("WITH_BEAMB") and env.getArg("WITH_BEAMB") == True:
    arguments.append(("--with-beamb", ""))
  if env.hasArg("JDKHOME"):
    arguments.append(("--jdkhome=", env.getArg("JDKHOME")))
  if env.hasArg("KEYSTORE"):
    arguments.append(("--keystore=", env.getArg("KEYSTORE")))

  for a in arguments:
    print "{0:25s} {1:35s}".format(a[0], a[1])

##
# Prints information about usage.
# @param brief if brief usage information should be shown or not
# @param msg (optional). If brief == True, then this text can be shown if provided
#
def usage(brief, msg=None):
  if brief == True:
    if msg != None:
      print msg
    print "Usage: setup <options> command, use --help for information"
  else:
    print """
NODE INSTALLER
Usage: setup <options> command, use --help for information

This is the alternate installer that eventually will replace 
the original baltrad-node setup scripts. The usage is basically 
the same as when using the previous setup commands but this 
script will install everything in one go.

The script will remember several configuration parameters between
runs but some of them will not be stored, like passwords and
similar items. If you want to use the previous parameters, then
you can specify --recall-last-args

Command:
Valid commands are:
 - install
     Installs the software
     
 - check
     Checks that the provided dependencies are correct

 - clean
     Cleans up everything

 - fetch
     Fetch all packages so that it is possible to run an installation
     in 'offline' mode. It will atempt to clean up any unessecary 
     content but it is suggested to execute clean prior fetch.
 
 - dist
     Create distribution tarball
     
Options:
--help
    Shows this text

--recall-last-args
    If you want to use the previous arguments, then you can use
    this option. It will try to restore the configuration parameters
    used in the last run. 

--nodename
    This attribute should really be specified but there is a default value which
    is the hostname as shown by the command 'hostname'.

--prefix=<prefix>
    Points out where the system should be installed. 
    [Default /opt/n2]
    
--tprefix=<prefix>
    Points out where the third-party software should be installed.
    [Default <prefix>/third_party]
    
--jdkhome=<jdkhome>
    Points out the jdkhome directory. If omitted, the installer will
    try to find a valid jdk.

--keystore=<path>
    Point out the keystore directory to use when configuring setting up the
    different modules for certification. If not specified, one will be
    created for you in $PREFIX/etc/bltnode-keystore.

--with-zlib=yes|no|<zlibroot>|<zlibinc>,<zliblib>
    Specifies if zlib should be built by the installer or not. 
    [Default yes]
    - 'yes' means that the installer should install the provided zlib
    - 'no' means that the installer should atempt to locate a valid
      zlib installation
    - zlibroot specifies a zlib installation where includes can be 
      found in <zlibroot>/include and libraries can be found in 
      <zlibroot>/lib
    - <zlibinc>,<zliblib> can be used to point out the specific 
      include and library paths

--with-psql=<psqlroot>|<psqlinc>,<psqllib>
    Specifies where to locate the postgresql include and library files.
    If omitted the install script assumes that they can be found in 
    the standard locations.
    - psqlroot specifies a postgres installation where includes can be 
      found in <psqlroot>/include and libraries can be found in <psqlroot>/lib
    - <psqlinc>,<psqllib> can be used to point out the specific 
      include and library paths

--dbuser=<user>
    Specifies the database user to use. 
    [Default baltrad]

--dbpwd=<pwd>
    Specifies the database user password to use. 
    [Default baltrad]
    
--dbname=<name>
    Specified the database name to use. 
    [Default baltrad]

--dbhost=<host>
    Specified the database host to use. 
    [Default 127.0.0.1]

--with-hdfjava=<hdf java root>
    Specifies the hdf java root installation directory. 
    If omitted, the installer will install it's own version of hdf-java.
    
--reinstalldb
    Reinstalls the database tables. Use with care.

--excludedb
    Ignores installation of the database tables. Might be since they
    already has been installed. This will cause the DBINSTALL package
    to be set as installed.
    
--runas=<user>
    Specifies the runas user for tomcat and other processes. It is not 
    allowed to use a runas user that is root due to security-issues. 
    [Defaults to user that is installing]

--datadir=<dir>
    The directory where all the data storage files should be placed for baltrad-db.
    [Default <prefix>/bdb_storage]

--urlrepo=<url>
    The url from where the url packages can be fetched.
    [Default http://git.baltrad.eu/blt_dependencies]
    
--gitrepo=<url>
    The url from where the baltrad node git packages can be fetched.
    [Default gitosis@git.baltrad.eu]

--with-rave
    Install the rave pgf

--rave-pgf-port=<port>
    Set the port rave should run on.
    [default: 8085]

--with-bufr
    Install the bufr software. This will also affect rave so that if
    we have specified bufr support rave will be built with bufr support
    enabled as well.

--rave-center-id=<id>
    Originating center id to be used by rave as the source of its products.
    [default: 82]

--rave-dex-spoe=<spoe>
    Dex's single point of entry to be used by rave. 
    [default: localhost:$TOMCATPORT
    
--with-rave-gmap
    Install the rave google map plugin. Will also cause rave pgf to be installed.

--with-bropo
    Install the anomaly detector bropo. Will also cause rave to be installed.

--with-beamb
    Install the beam blockage detector beamb. Will also cause rave to be installed.

--with-bdbfs
    Will build and install the baltrad db file system driver

--bdb-port=8090
    BDB server port

--bdb-pool-max-size=<N>
    Set the pool size for bdb connections to <N>
    [default: 10]

--rebuild=<module1>,<module2>,...
    Will force a rebuild and installation of the specified modules. To get a 
    list of available modules and their versions. See option --print-modules.
    E.g. --rebuild=TOMCAT,RAVE
    
--print-modules
    Prints all available modules and their respective version.
    
--print-config
    Prints the build configuration
    
--exclude-tomcat
    Will exclude installation of tomcat. This is not a recommended procedure but 
    it is here for the possibility to use your own tomcat installation if it 
    is necessary.

--tomcatport=<port>
    Specifies the port on which the tomcat installation should listen on.
    Don't use together with --tomcaturl. 
    [Default 8080]

--tomcaturl=<url>
    Specifies the tomcat url where the tomcat installation resides. Don't
    use together with --tomcatport. 
    [Default http://localhost:8080]
    
--tomcatpwd=<pwd>
    Specifies the password that should be used for the manager in the tomcat
    installation.
    
--force
    Unused at the moment
    
--experimental
    When running into problems with building, like missing libraries, link problems
    or other miscellaneous problems. This might be the option to specify. Some modules
    are currently beeing evaluated if they are stable enough to be used in production
    and by specifying this option these modules will be built instead.
"""

def parse_buildzlib_argument(arg):
  if arg.lower() == "no" or arg.lower() == "false":
    return False, None, None
  elif arg.lower() == "yes" or arg.lower() == "true":
    return True, None, None
  
  tokens = arg.split(",")
  if len(tokens) == 2:
    return False, tokens[0], tokens[1]
  elif len(tokens) == 1:
    return False, "%s/include"%tokens[0], "%s/lib"%tokens[0] 
  else:
    raise InstallerException, "--zlib should either be (no, yes, <libroot> or <inc>,<lib> where <inc> and/or <lib> may be empty"

def handle_tomcat_arguments(benv):
  if benv.hasArg("TOMCATPORT") and benv.hasArg("TOMCATURL"):
    # Verify that port does not conflict
    from urlparse import urlparse
    a = urlparse(benv.getArg("TOMCATURL"))
    if a.port == None or "%s"%a.port != benv.getArg("TOMCATPORT"):
      raise InstallerException, "tomcatport and tomcaturl port differs"
  elif benv.hasArg("TOMCATPORT"):
    benv.addArg("TOMCATURL", "http://localhost:%s"%benv.getArg("TOMCATPORT"))
  elif benv.hasArg("TOMCATURL"):
    from urlparse import urlparse
    a = urlparse(benv.getArg("TOMCATURL"))
    if a.port == None:
      raise InstallerException, "You must specify port in tomcat url"
    benv.addArg("TOMCATPORT", "%d"%a.port)
  else:
    benv.addArg("TOMCATPORT", "8080")
    benv.addArg("TOMCATURL", "http://localhost:%s"%benv.getArg("TOMCATPORT"))  
  

def parse_buildpsql_argument(arg):
  tokens = arg.split(",")
  if len(tokens) == 2:
    psqlinc = tokens[0]
    psqllib = tokens[1]
  elif len(tokens) == 1:
    psqlinc = "%s/include"%tokens[0]
    psqllib = "%s/lib"%tokens[0]
  else:
    raise InstallerException, "--with-psql should either be <inc>,<lib> or <root>"
  
  if not os.path.isdir(psqlinc):
    raise InstallerException, "Provided path (%s) does not seem to be be used as an include path."%psqlinc
  if not os.path.isdir(psqllib):
    raise InstallerException, "Provided path (%s) does not seem to be be used as an lib path."%psqllib
  
  return psqlinc, psqllib
  
if __name__=="__main__":
  import getpass
  optlist = []
  args = []
  
  try:
    optlist, args = getopt.getopt(sys.argv[1:], 'x', 
                                  ['prefix=','tprefix=','jdkhome=','with-zlib=',
                                   'with-psql=','with-bufr', 'with-rave','with-rave-gmap','with-bropo','with-beamb',
                                   'with-hdfjava=', 'with-bdbfs','rebuild=',
                                   'bdb-pool-max-size=', "bdb-port=",
                                   'rave-pgf-port=', "rave-center-id=", "rave-dex-spoe=",
                                   'dbuser=', 'dbpwd=','dbname=','dbhost=','keystore=','nodename=',
                                   'reinstalldb','excludedb', 'runas=','datadir=','warfile=',
                                   'urlrepo=','gitrepo=','offline',
                                   'print-modules', 'print-config', 'exclude-tomcat', 'recall-last-args',
                                   'experimental',
                                   'force','tomcatport=','tomcaturl=','tomcatpwd=','help'])
  except getopt.GetoptError, e:
    usage(True, e.__str__())
    sys.exit(127)
  
  dorestore = False
  doprintconfig = False
  doprintmodules = False
  
  # First handle help and printouts misc options so that we don't get stuck on
  # any bad configuration properties.
  for o,a in optlist:
    if o == "--help":
      usage(False)
      sys.exit(0)
    elif o == "--print-modules":
      doprintmodules = True
    elif o == "--recall-last-args":
      dorestore = True
    elif o == "--print-config":
      doprintconfig = True
      
  env = buildenv()
  if dorestore:
    env.restore()
  
  env.excludeModule("RAVE")
  env.excludeModule("RAVE-GMAP")
  env.excludeModule("BROPO")
  env.excludeModule("BBUFR")
  env.excludeModule("BEAMB")
  
  reinstalldb=False
  rebuild = []
  experimental_build=False
  
  for o, a in optlist:
    if o == "--prefix":
      env.addArg("PREFIX", a)
    elif o == "--tprefix":
      env.addArg("TPREFIX", a)
    elif o == "--jdkhome":
      env.addArg("JDKHOME", a)
    elif o == "--dbuser":
      env.addArg("DBUSER", a)
    elif o == "--dbpwd":
      env.addArgInternal("DBPWD", a)
    elif o == "--dbname":
      env.addArg("DBNAME", a)
    elif o == "--dbhost":
      env.addArg("DBHOST", a)
    elif o == "--nodename":
      env.addArg("NODENAME", a)
    elif o == "--keystore":
      env.addArg("KEYSTORE", a)
    elif o == "--rebuild":
      rebuild = a.split(",")
    elif o == "--with-zlib":
      env.addArg("ZLIBARG", a)
    elif o == "--with-psql":
      env.addArg("PSQLARG", a)
    elif o == "--with-hdfjava":
      if not os.path.isdir(a):
        print "--with-hdfjava must be provided with the root directory of the hdf-java installation"
        sys.exit(127)
      else:
        env.addArg("HDFJAVAHOME", a)
    elif o == "--exclude-tomcat":
      env.excludeModule("TOMCAT")
    elif o == "--tomcatport":
      env.addArg("TOMCATPORT", a)
    elif o == "--tomcaturl":
      env.addArg("TOMCATURL", a)
    elif o == "--tomcatpwd":
      env.addArgInternal("TOMCATPWD", a)
    elif o == "--with-bdbfs":
      env.addArg("BUILD_BDBFS", "yes")
    elif o == "--bdb-pool-max-size":
      env.addArg("BDB_POOL_MAX_SIZE", a)
    elif o == "--bdb-port":
      env.addArg("BDB_PORT", a)
    elif o == "--with-bufr":
      env.addArg("WITH_BBUFR", True)
    elif o == "--with-rave":
      env.addArg("WITH_RAVE", True)
    elif o == "--rave-pgf-port":
      env.addArg("RAVE_PGF_PORT", a)
    elif o == "--rave-center-id":
      env.addArg("RAVE_CENTER_ID", a)
    elif o == "--rave-dex-spoe":
      env.addArg("RAVE_DEX_SPOE", a)
    elif o == "--with-rave-gmap":
      env.addArg("WITH_RAVE_GMAP", True)
    elif o == "--with-bropo":
      env.addArg("WITH_BROPO", True)
    elif o == "--with-beamb":
      env.addArg("WITH_BEAMB", True)
    elif o == "--reinstalldb":
      reinstalldb=True
      env.addArgInternal("REINSTALLDB", True)
    elif o == "--excludedb":
      env.addArgInternal("EXCLUDEDB", True)
    elif o == "--offline":
      env.addArgInternal("INSTALL_OFFLINE", True)
    elif o == "--runas":
      env.addArg("RUNASUSER", a)
    elif o == "--datadir":
      env.addArg("DATADIR", a)
    elif o == "--warfile":
      env.addArgInternal("WARFILE", a)
    elif o == "--urlrepo":
      env.addArg("URLREPO", a)
    elif o == "--gitrepo":
      env.addArg("GITREPO", a)
    elif o == "--help":
      pass
    elif o == "--print-modules":
      pass
    elif o == "--print-config":
      pass
    elif o == "--recall-last-args":
      pass
    elif o == "--experimental":
      experimental_build = True
    else:
      usage(True, "Unsupported argument: %s"%o)
      sys.exit(127)

  if not env.hasArg("TOMCATPWD"):
    print "--tomcatpwd not specified, please specify password."
    pwd = None
    while pwd == None:
      pwd1 = raw_input("Enter password: ")
      pwd2 = raw_input("Again: ")
      if pwd1 == pwd2:
        pwd = pwd1
      else:
        print "Passwords not matching"
    env.addArgInternal("TOMCATPWD", pwd)

  # set defaults for whatever arguments we didn't get from the user
  env.addUniqueArg("PREFIX", "/opt/baltrad")
  env.addUniqueArg("TPREFIX", env.expandArgs("${PREFIX}/third_party"))
  env.addUniqueArg("URLREPO", "http://git.baltrad.eu/blt_dependencies")
  env.addUniqueArg("GITREPO", "gitosis@git.baltrad.eu")
  env.addUniqueArg("HDFJAVAHOME", env.expandArgs("${TPREFIX}/hdf-java"))
  env.addUniqueArg("DBUSER", "baltrad")
  env.addUniqueArgInternal("DBPWD", "baltrad")
  env.addUniqueArg("DBNAME", "baltrad")
  env.addUniqueArg("DBHOST", "127.0.0.1")
  env.addUniqueArg("BUILD_BDBFS", "no")
  env.addUniqueArg("RUNASUSER", getpass.getuser())
  env.addUniqueArg("KEYSTORE", env.expandArgs("${PREFIX}/etc/bltnode-keys"))
  
  if not env.hasArg("NODENAME"):
    import socket
    nodename = socket.gethostname()
    print "NODENAME WASN'T SPECIFIED, DEFAULTING TO: %s"%nodename
    env.addArg("NODENAME", nodename)
  
  #
  # We must ensure that the tomcatport and tomcaturl port is not conflicting
  # and that the tomcat arguments always are there.
  #
  handle_tomcat_arguments(env)
  
  env.addUniqueArg("BDB_POOL_MAX_SIZE", "10")
  env.addUniqueArg("BDB_PORT", "8090")
  env.addUniqueArg("RAVE_PGF_PORT", "8085")
  env.addUniqueArg("RAVE_CENTER_ID", "82")
  env.addUniqueArg("RAVE_DEX_SPOE", env.expandArgs("localhost:${TOMCATPORT}"))

  #
  # If we are running in experimental mode, then mark all affected installers with
  # that information.
  #
  if experimental_build:
    for m in MODULES:
      if isinstance(m, experimental):
        m.setExperimentalMode(True)

  #
  # Print the configuration settings
  #
  if doprintconfig or doprintmodules:
    if doprintconfig:
      print "CONFIGURATION PARAMETERS"
      print_arguments(env)
      print ""
    if doprintmodules:
      print "MODULES"
      print_modules(env)
      print ""
    
    if len(args) == 0:
      sys.exit(0)
  
  env.remember() # Remember the previous arguments

  if len(args) != 1:
    usage(True, "You can only specify one command %s"%`args`)
    sys.exit(127)
  
  if args[0] not in ["install", "check", "clean", "fetch", "dist"]:
    usage(True, "Unknown command %s"%`args[0]`)
    sys.exit(127)

  if env.hasArg("WITH_BBUFR") and env.getArg("WITH_BBUFR") == True:
    env.removeExclude("BBUFR")

  if env.hasArg("WITH_RAVE") and env.getArg("WITH_RAVE") == True:
    env.removeExclude("RAVE")

  if env.hasArg("WITH_RAVE_GMAP") and env.getArg("WITH_RAVE_GMAP") == True:
    env.removeExclude("RAVE")
    env.removeExclude("RAVE-GMAP")

  if env.hasArg("WITH_BROPO") and env.getArg("WITH_BROPO") == True:
    env.removeExclude("RAVE")
    env.removeExclude("BROPO")
    
  if env.hasArg("WITH_BEAMB") and env.getArg("WITH_BEAMB") == True:
    env.removeExclude("RAVE")
    env.removeExclude("BEAMB")
    
  if env.hasArg("ZLIBARG"):
    buildzlib, zinc, zlib = parse_buildzlib_argument(env.getArg("ZLIBARG"))
    env.addArgInternal("ZLIBINC", zinc)
    env.addArgInternal("ZLIBLIB", zlib)
    if buildzlib == False:
      env.excludeModule("ZLIB")
  
  if env.hasArg("PSQLARG"):
    psqlinc, psqllib = parse_buildpsql_argument(env.getArg("PSQLARG"))
    env.addArgInternal("PSQLINC", psqlinc)
    env.addArgInternal("PSQLLIB", psqllib)
  
  if args[0] in ["install", "check"]:
    for validator in [jdkvalidator(), zlibvalidator(), psqlvalidator(), doxygenvalidator()]:
      validator.validate(env)

    if not env.hasArg("JDKHOME"):
      print "You must specify --jdkhome=... when installing the node"
      sys.exit(127)

  # bdb storage needs a data directory 
  if not env.hasArg("DATADIR"):
    env.addArg("DATADIR", env.expandArgs("$PREFIX/bdb_storage"))

  if args[0] in ["install"]:
    # Setup the general ld library path that will be the one pointing out
    # all relevant libraries when the system has been installed
    #
    ldpath = "$TPREFIX/lib"
    ldpath = "$HDFJAVAHOME/lib/linux:%s"%ldpath
    ldpath = "%s:$PREFIX/hlhdf/lib"%ldpath
    if not env.isExcluded("BBUFR"):
      ldpath = "%s:$PREFIX/bbufr/lib"%ldpath
    ldpath = "%s:$PREFIX/baltrad-db/lib"%ldpath
    ldpath = "%s:$PREFIX/lib"%ldpath
    if env.hasArg("PSQLLIB") and env.getArg("PSQLLIB") != None:
      ldpath = "%s:$PSQLLIB"%ldpath
    if env.hasArg("ZLIBLIB") and env.getArg("ZLIBLIB") != None:
      ldpath = "%s:$ZLIBLIB"%ldpath
  
    env.setLdLibraryPath("%s:$$LD_LIBRARY_PATH"%ldpath)

    # And setup the path as well
    pth="$TPREFIX/bin"
    pth="%s:$PREFIX/bin"%pth
    pth="%s:$PREFIX/hlhdf/bin"%pth
    pth="%s:$PREFIX/beast/bin"%pth
    pth="%s:$PREFIX/baltrad-db/bin"%pth

    env.setPath("%s:$$PATH"%pth)

    # We want to wrap everything up in some scripts
    # so that we can stop/start the node
    sldpath = ldpath
    if not env.isExcluded("BEAMB"):
      sldpath = "$PREFIX/beamb/lib:%s"%sldpath

    if not env.isExcluded("BROPO"):
      sldpath = "$PREFIX/bropo/lib:%s"%sldpath
      
    if not env.isExcluded("RAVE"):
      sldpath = "$PREFIX/rave/lib:%s"%sldpath
  
    spath = pth
    if not env.isExcluded("RAVE"):
      spath = env.expandArgs("$PREFIX/rave/bin:%s"%pth)

#    script = nodescripts(
#      "%s:$$PATH"%spath,
#      "%s:$$LD_LIBRARY_PATH"%sldpath,
#      "1.0.0",
#      raveinstalled=not env.isExcluded("RAVE")
#    )
    script = nodescripts(
      "%s"%spath,
      "%s"%sldpath,
      "1.0.0",
      raveinstalled=not env.isExcluded("RAVE")
    )

    script.create_scripts(env)
    env.setNodeScript(script)

  # Set the installer path
  env.setInstallerPath(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))

  if args[0] in ["install"]:
    if reinstalldb == True:
      if not "DBINSTALL" in rebuild:
        rebuild.append("DBINSTALL")

  ni = node_installer(MODULES, rebuild)
  if args[0] == "install":
    ni.install(env)
  elif args[0] == "check":
    pass
  elif args[0] == "clean":
    ni.clean(env)
  elif args[0] == "fetch":
    ni.fetch_offline_content(env)
  elif args[0] == "dist":
    ni.create_offline_tarball(env)
