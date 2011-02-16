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
from hlhdfinstaller import hlhdfinstaller
from bdbinstaller import bdbinstaller
from beastinstaller import beastinstaller
from dexinstaller import dexinstaller
from raveinstaller import raveinstaller
from ravegmapinstaller import ravegmapinstaller
from dbinstaller import dbinstaller, dbupgrader
from nodescripts import nodescripts
from deployer import deployer
from scriptinstaller import scriptinstaller

from node_package import node_package

from extra_functions import *
from node_installer import node_installer

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
MODULES=[cmmi(package("ZLIB", "1.2.4",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/zlib-1.2.4.tar.gz"), "zlib-1.2.4", True)),
              "--prefix=\"${TPREFIX}\"", False, True,
              foptionalarg=zlib_optional_arg),

         cmmi(package("HDF5", "1.8.5-patch1",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/hdf5-1.8.5-patch1.tar.gz"), "hdf5-1.8.5-patch1", True),
                      depends=["ZLIB"]),
              "--prefix=\"$TPREFIX\" --with-pthread=yes --enable-threadsafe", False, True,
              foptionalarg=hdf5_optional_zlib_arg),
              
         cmmi(package("EXPAT", "2.0.1",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/expat-2.0.1.tar.gz"), "expat-2.0.1", True)),
              "--prefix=\"$TPREFIX\"", False, True),
              
         cmmi(package("PROJ.4", "4.7.0",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/proj-4.7.0.tar.gz"), "proj-4.7.0", True)),
              "--prefix=\"$TPREFIX\" --with-jni=\"$JDKHOME/include\"", False, True,
              osenv({"CFLAGS":"-I\"$JDKHOME/include/linux\""})),
              
         cmmi(package("PYTHON", "2.6.4",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/Python-2.6.4.tgz"), "Python-2.6.4", True)),
              "--prefix=\"$TPREFIX\" --enable-shared", False, True),

         shinstaller(package("NUMPY", "1.3.0",
                             untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/numpy-1.3.0.tar.gz"), "numpy-1.3.0", True),
                             depends=["PYTHON"]),
                     "\"$TPREFIX/bin/python\" setup.py install",
                     osenv({"LD_LIBRARY_PATH":"$TPREFIX/lib"})),
                     
         shinstaller(package("PYSETUPTOOLS", "0.6c11",
                             nodir(urlfetcher("http://git.baltrad.eu/blt_dependencies/setuptools-0.6c11-py2.6.egg")),
                             depends=["PYTHON"]),
                     "sh setuptools-0.6c11-py2.6.egg",
                     osenv({"LD_LIBRARY_PATH":"$TPREFIX/lib", "PATH":"$TPREFIX/bin:$$PATH"})),
                     
         pilinstaller(package("PIL", "1.1.7",
                              untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/Imaging-1.1.7.tar.gz"), "Imaging-1.1.7", True),
                              depends=["PYTHON","ZLIB"])),
         
         cmmi(package("CURL", "7.19.0",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/curl-7.19.0.tar.gz"), "curl-7.19.0", True)),
              "--prefix=\"$TPREFIX\"", False, True),
              
         shinstaller(package("PYCURL", "7.19.0",
                             untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/pycurl-7.19.0.tar.gz"), "pycurl-7.19.0", True),
                             depends=["PYTHON","CURL"]),
                     "\"$TPREFIX/bin/python\" setup.py install",
                     osenv({"LD_LIBRARY_PATH":"$TPREFIX/lib", "PATH":"$TPREFIX/bin:$$PATH"})),
         
         tomcatinstaller(package("TOMCAT", "6.0.26",
                                 untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/apache-tomcat-6.0.26.tar.gz"), "apache-tomcat-6.0.26", True))),
         
         hdfjavainstaller(package("HDFJAVA", "2.6.1",
                                  machinefetcher({
                                    'i386':untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/hdf-java-2.6.1-i386-bin.tar"), "hdf-java", False),
                                    'x86_64':untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/hdf-java-2.6.1-x86_64-bin.tar"), "hdf-java", False)}
                                  ))),
         
         shinstaller(package("ANT", "1.8.0",
                             untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/apache-ant-1.8.0-bin.tar.gz"), ".", True)),
                     "rm -fr \"$TPREFIX/ant\"; mv -f apache-ant-1.8.0 \"$TPREFIX/ant\""),
                     
         shinstaller(package("BOOST", "1.42.0",
                             untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/boost_1_42_0.tar.gz"), "boost_1_42_0", True)),
                     "./bootstrap.sh --prefix=\"$TPREFIX\" --with-python=\"$TPREFIX/bin/python\" --without-icu --with-libraries=filesystem,program_options,thread && ./bjam install"), 

         cmmi(package("PQXX", "3.1",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/libpqxx-3.1.tar.gz"), "libpqxx-3.1", True)),
              "--prefix=\"$TPREFIX\" --enable-shared", False, True),

         cmmi(package("SWIG", "1.3.40",
                      untar(urlfetcher("http://git.baltrad.eu/blt_dependencies/swig-1.3.40.tar.gz"), "swig-1.3.40", True)),
              "--prefix=\"$TPREFIX\" --with-java=\"$JDKHOME/bin/java\" --with-javac=\"$JDKHOME/bin/javac\" --with-javaincl=\"$JDKHOME/include\" --with-python=\"$TPREFIX/bin/python\"", False, True),
              
         hdfjavasetupinstaller(package("HDFJAVASETUP", "2.6.1", depends=["TOMCAT", "HDFJAVA"])),
         
         # Time to install baltrad node software
         hlhdfinstaller(node_package("HLHDF", depends=["ZLIB", "HDF5"])),

         bdbinstaller(node_package("BALTRAD-DB", depends=["ZLIB", "HDF5", "HLHDF", "PQXX"])),
         
         beastinstaller(node_package("BEAST", depends=["BALTRAD-DB"])),
         
         dexinstaller(node_package("BALTRAD-DEX", depends=["HDFJAVA", "TOMCAT", "BALTRAD-DB", "BEAST"])),
         
         raveinstaller(node_package("RAVE", depends=["EXPAT", "PROJ.4", "PYTHON", "NUMPY", "PYSETUPTOOLS", "PYCURL", "HLHDF"])),
         
         ravegmapinstaller(node_package("RAVE-GMAP", depends=["RAVE"])), #Just use rave as dependency, rest of dependencies will trigger rave rebuild
         
         dbinstaller(package("DBINSTALL", "1.0", nodir())),
         
         dbupgrader(package("DBUPGRADE", "1.0", nodir(), remembered=False)),

         deployer(package("DEPLOY", "1.0", nodir(), depends=["BALTRAD-DEX"], remembered=False)),

         scriptinstaller(package("SCRIPT", "1.0", nodir(), remembered=False)),
        ]

##
# Prints information about usage.
# @param brief if brief usage information should be shown or not
# @param msg (optional). If brief == True, then this text can be shown if provided
#
def usage(brief, msg=None):
  if brief == True:
    if msg != None:
      print msg
    print "Usage: install.py <options>, use --help for information"
  else:
    print """
NODE INSTALLER
  
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
                                  ['prefix=','tprefix','jdkhome=','with-zlib=',
                                   'with-psql=','with-rave','with-rave-gmap',
                                   'with-hdfjava=', 'with-bdbfs','rebuild=',
                                   'dbuser=', 'dbpwd=','dbname=','dbhost=',
                                   'reinstalldb','runas=','datadir=',
                                   'force','tomcatport=','tomcaturl=','tomcatpwd=','help'])
  except getopt.GetoptError, e:
    usage(True, e.__str__())
    sys.exit(127)
    
  env = buildenv()
  env.addArg("PREFIX", "/opt/n2")
  env.addArg("TPREFIX", "/opt/n2/third_party")
  env.addArg("TOMCATPWD", "secret")
  env.addArg("HDFJAVAHOME", "/opt/n2/third_party/hdf-java")
  env.addArg("DBUSER", "baltrad")
  env.addArg("DBPWD", "baltrad")
  env.addArg("DBNAME", "baltrad")
  env.addArg("DBHOST", "127.0.0.1")
  env.addArg("BUILD_BDBFS", "no")
  env.addArg("RUNASUSER", getpass.getuser())
  env.excludeModule("RAVE")
  env.excludeModule("RAVE-GMAP")
  
  reinstalldb=False
  rebuild = []
  
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
      env.addArg("DBPWD", a)
    elif o == "--dbname":
      env.addArg("DNAME", a)
    elif o == "--dbhost":
      env.addArg("DBHOST", a)
    elif o == "--rebuild":
      rebuild = a.split(",")
    elif o == "--with-zlib":
      buildzlib, zinc, zlib = parse_buildzlib_argument(a)
      env.addArg("ZLIBINC", zinc)
      env.addArg("ZLIBLIB", zlib)
      if buildzlib == False:
        env.excludeModule("ZLIB")
    elif o == "--with-psql":
      psqlinc, psqllib = parse_buildpsql_argument(a)
      env.addArg("PSQLINC", psqlinc)
      env.addArg("PSQLLIB", psqllib)
    elif o == "--with-hdfjava":
      if not os.path.isdir(a):
        print "--with-hdfjava must be provided with the root directory of the hdf-java installation"
        sys.exit(127)
      else:
        env.addArg("HDFJAVAHOME", a)
    elif o == "--tomcatport":
      env.addArg("TOMCATPORT", a)
    elif o == "--tomcaturl":
      env.addArg("TOMCATURL", a)
    elif o == "--tomcatpwd":
      env.addArg("TOMCATPWD", a)
    elif o == "--with-bdbfs":
      env.addArg("BUILD_BDBFS", "yes")
    elif o == "--with-rave":
      env.removeExclude("RAVE")
    elif o == "--with-rave-gmap":
      env.removeExclude("RAVE")
      env.removeExclude("RAVE-GMAP")
    elif o == "--reinstalldb":
      reinstalldb=True
      env.addArg("REINSTALLDB", True)
    elif o == "--runas":
      env.addArg("RUNASUSER", a)
    elif o == "--datadir":
      env.addArg("DATADIR", a)
    elif o == "--help":
      usage(False)
      sys.exit(0)
    else:
      usage(True, "Unsupported argument: %s"%o)
      sys.exit(127)

  for validator in [jdkvalidator(), zlibvalidator(), psqlvalidator()]:
    validator.validate(env)

  if not env.hasArg("JDKHOME"):
    print "You must specify --jdkhome=... when installing the node"
    sys.exit(127)

  # bdb storage needs a data directory 
  if not env.hasArg("DATADIR"):
    env.addArg("DATADIR", env.expandArgs("$PREFIX/bdb_storage"))

  # Ensure that we don't have conflicting information in the tomcatport
  # and the tomcaturl
  if env.hasArg("TOMCATPORT") and env.hasArg("TOMCATURL"):
    raise InstallerException, "Don't specify both tomcatport and tomcaturl"
  elif env.hasArg("TOMCATPORT"):
    env.addArg("TOMCATURL", "http://localhost:%s"%env.getArg("TOMCATPORT"))
  elif env.hasArg("TOMCATURL"):
    from urlparse import urlparse
    a = urlparse(env.getArg("TOMCATURL"))
    if a.port == None:
      raise InstallerException, "You must specify port in tomcat url"
    env.addArg("TOMCATPORT", "%d"%a.port)
  else:
    env.addArg("TOMCATPORT", "8080")
    env.addArg("TOMCATURL", "http://localhost:%s"%env.getArg("TOMCATPORT"))

  # Setup the general ld library path that will be the one pointing out
  # all relevant libraries when the system has been installed
  #
  ldpath = "$TPREFIX/lib"
  ldpath = "$HDFJAVAHOME/lib/linux:%s"%ldpath
  ldpath = "%s:$PREFIX/hlhdf/lib"%ldpath
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

  # Set the installer path
  env.setInstallerPath(os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0]))))

  # We want to wrap everything up in some scripts
  # so that we can stop/start the node
  sldpath = ldpath
  if not env.isExcluded("RAVE"):
    sldpath = env.expandArgs("$PREFIX/rave/lib:%s"%ldpath)
  
  spath = pth
  if not env.isExcluded("RAVE"):
    spath = env.expandArgs("$PREFIX/rave/bin:%s"%pth)
      
  script = nodescripts("%s:$$PATH"%spath, "%s:$$LD_LIBRARY_PATH"%sldpath, "1.0.0")
  script.create_scripts(env)
  env.setNodeScript(script)

  if reinstalldb == True:
    if not "DBINSTALL" in rebuild:
      rebuild.append("DBINSTALL")

  ni = node_installer(MODULES, rebuild)
  ni.install(env)
