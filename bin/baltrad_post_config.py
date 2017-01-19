#!/usr/bin/env python
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

Script for performing post configuration of the baltrad node installation. It will manage generation of
property files and allowing for creation or upgrading of the database.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2013-02-11
'''
import sys, os, subprocess, tempfile, re
import shutil
import jprops
import psycopg2, psycopg2.extensions

# The pattern for identifying the database information
# so that we can use the psycopg2 syntax for establish a connection to the
# database
PGSQL_PATTERN = re.compile("postgresql://([^:]+):([^@]+)@([^/]+)/([^$]+)")

##
# The class that provides support for creating, upgrading and dropping all
# tables associated with baltrad
#
class baltrad_database(object):
  _prefix = None
  _propertyfile = None
  _username=None
  _password=None
  _hostname=None
  _dbname=None

  ##
  # Constructor
  # @param prefix: install root
  # @param propertyfile: the property file used by baltrad-bdb-client
  # @param hostname: the host name of the database
  # @param dbname: the name of the database
  # @param username: the user owning the database
  # @param password: the password for the user
  def __init__(self, prefix, propertyfile, hostname, dbname, username, password):
    self._prefix = prefix
    self._propertyfile = propertyfile
    self._hostname = hostname
    self._dbname = dbname
    self._username = username
    self._password = password
    
  ##
  # Creates the database tables
  #
  def create(self):
    self._create_bdb()
    self._create_beast()
    self._create_dex()

  ##
  # Upgrades the database tables
  #
  def upgrade(self):
    self._upgrade_bdb()
    self._upgrade_beast()
    self._upgrade_dex()

  ##
  # Updates the admin users password
  def update_admin_password(self, password):
    connection = psycopg2.connect("host=%s dbname=%s user=%s password=%s"%(self._hostname,self._dbname,self._username,self._password))
    try:
      dbcursor = connection.cursor()
      dbcursor.execute("UPDATE dex_users SET PASSWORD=MD5('"+password+"') WHERE name='admin'")
      connection.commit()
    except psycopg2.DatabaseError, e:
      raise Exception, "Failed to run baltrad %s db scheme, e: %s"%(id, e.__str__())
    finally:
      if dbcursor:
        dbcursor.close()
      if connection:
        connection.close()
    
    
  ##
  # Creates the bdb tables
  def _create_bdb(self):
    cmd = "%s/baltrad-db/bin/baltrad-bdb-create"%self._prefix
    conf = "--conf=%s"%self._propertyfile
    ocode = subprocess.call([cmd, conf])
    if ocode != 0:
      raise Exception, "Failed to create baltrad bdb"
  
  ##
  # Upgrades the bdb tables
  def _upgrade_bdb(self):
    cmd = "%s/baltrad-db/bin/baltrad-bdb-upgrade"%self._prefix
    conf = "--conf=%s"%self._propertyfile
    ocode = subprocess.call([cmd, conf])
    if ocode != 0:
      raise Exception, "Failed to create baltrad bdb"
  
  ##
  # Creates the beast tables
  def _create_beast(self):
    self._run_sql_script("%s/beast/sql/create_db.sql"%self._prefix, "create beast")

  ##
  # Upgrades the beast tables
  def _upgrade_beast(self):
    self._run_sql_script("%s/beast/sql/upgrade_db.sql"%self._prefix, "upgrade beast")

  ##
  # Creates the dex tables
  def _create_dex(self):
    self._run_sql_script("%s/BaltradDex/sql/create_dex_schema.sql"%self._prefix, "create dex")
    self._run_sql_script("%s/BaltradDex/sql/insert_default_dex_data.sql"%self._prefix, "create dex data")

  ##
  # Upgrades the dex tables 
  def _upgrade_dex(self):
    self._run_sql_script("%s/BaltradDex/sql/upgrade_dex_schema.sql"%self._prefix, "upgrade dex")
  
  ##
  # Runs the specified sql script. The id is just used for identifying what is beeing run
  # @param scriptname: The filename of the sql script to be executed
  # @param id: The id to be used in the error messages
  def _run_sql_script(self, scriptname, id):
    sql = open(scriptname, 'r').read()
    connection = psycopg2.connect("host=%s dbname=%s user=%s password=%s"%(self._hostname,self._dbname,self._username,self._password))
    try:
      dbcursor = connection.cursor()
      dbcursor.execute(sql)
      connection.commit()
    except psycopg2.DatabaseError, e:
      raise Exception, "Failed to run baltrad %s db scheme, e: %s"%(id, e.__str__())
    finally:
      if dbcursor:
        dbcursor.close()
      if connection:
        connection.close()

##
# The baltrad post configurator
#
class baltrad_post_config(object):
  _config = None
  _installdb = False
  _upgradedb = False
  
  ##
  # Constructor
  # @param config the configuration file
  def __init__(self, config, installdb, upgradedb, password=None):
    self._config = config
    self._installdb = installdb
    self._upgradedb = upgradedb
    self._password = password

  ##
  # Load the properties in the property file cfile into a dictionary
  # @param cfile the property file name
  # @return the properties
  #
  def _load_properties(self, cfile):
    with open(cfile) as fp:
      return jprops.load_properties(fp)

  ##
  # Utility for reading a property from properties and then save that property
  # to another file. If property does not exist in properties, a default value is used.
  # @param fp: the file pointer
  # @param properties: the properties dictionary
  # @param propname: the name of the property
  # @param default: default value 
  def _write_property_to_file(self, fp, properties, propname, default):
    if properties.has_key(propname):
      fp.write("%s = %s\n"%(propname, properties[propname]))
    else:
      fp.write("%s = %s\n"%(propname, default))

  ##
  # Converts a bltnode.properties file into a post configuration file.
  # @param nodeprops: The bltnode properties file
  # 
  def export(self, nodeprops):
    properties = self._load_properties(nodeprops)
    dburimatcher = PGSQL_PATTERN.match(properties["baltrad.bdb.server.backend.sqla.uri"])
    if not dburimatcher:
      raise Exception, "Can not parse the database information from baltrad.bdb.server.backend.sqla.uri"
    
    with open(self._config, "w") as fp:
      fp.write("\n#General configuration settings\n")
      fp.write("baltrad.install.root = /opt/baltrad\n")
      fp.write("baltrad.install.3p_root = /opt/baltrad/third_party\n")
      fp.write("# Specifies if rave is installed or not (true, false).\n")
      fp.write("# Used to know if rave_defines.py should be configured or not.\n")
      fp.write("baltrad.with.rave = true\n\n")
      
      fp.write("# postgres database specifics\n")
      fp.write("baltrad.db.username = %s\n"%dburimatcher.group(1))
      fp.write("baltrad.db.password = %s\n"%dburimatcher.group(2))
      fp.write("baltrad.db.hostname = %s\n"%dburimatcher.group(3))
      fp.write("baltrad.db.dbname = %s\n"%dburimatcher.group(4))
      fp.write("\n")
      fp.write("baltrad.node.name = %s\n"%properties["baltrad.beast.pgf.nodename"])
      fp.write("baltrad.keyczar.root = %s\n"%properties["baltrad.bdb.server.auth.keyczar.keystore_root"])
      fp.write("baltrad.dex.uri = %s\n"%properties["baltrad.beast.server.url"])
            
      fp.write("\n\n#BDB settings\n")
      fp.write("#baltrad.bdb.server.type = werkzeug\n")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.type", "cherrypy")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.threads", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.backlog", "5")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.timeout", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.uri", "http://localhost:8090")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.type", "sqla")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.pool_size", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.log.level", "INFO")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.storage.type", "db")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.auth.providers", "noauth, keyczar")

      fp.write("\n\n")
      fp.write("# Additional post config scripts.\n")
      fp.write("# These scripts are called as python scripts with the only additional argument pointing at this\n")
      fp.write("# property file so you can specify more properties in addition to the ones above.\n")
      fp.write("# The naming of the post config script properties should be baltrad.post.config.script.<N> \n")
      fp.write("# where N is a sequential number running from 1, and upward (1,2,3....).\n")
      fp.write("#baltrad.post.config.script.1=..../xyz.py\n")
      fp.write("#baltrad.post.config.script.2=..../xyz2.py\n")
      
    fp.close()

  ##
  # Configures a node from the post configuration file
  #
  def setup(self):
    properties = self._load_properties(self._config)
    self._configure_bltnode_properties(properties)
    self._configure_dex_properties(properties)
    self._configure_dex_db_properties(properties)
    self._configure_dex_fc_properties(properties)
    if properties.has_key("baltrad.with.rave") and properties["baltrad.with.rave"].lower() == "true":
      self._configure_rave(properties)
  
    if self._installdb:
      self._create_database(properties)
    if self._upgradedb:
      self._upgrade_database(properties)
    if self._password:
      self._update_admin_password(properties)
    self._run_plugins(properties)
  
  def _run_plugins(self, properties):
    index = 1
    while properties.has_key("baltrad.post.config.script.%d"%index):
      script = properties["baltrad.post.config.script.%d"%index]
      code = subprocess.call(["python", script, self._config])
      if code != 0:
        print "Failed to run post script: %s"%script
      index = index + 1
    
  ##
  # Creates the database tables
  #
  def _create_database(self, properties):
    prefix = properties["baltrad.install.root"]
    propertyfile = "%s/etc/bltnode.properties"%prefix
    hostname = properties["baltrad.db.hostname"]
    dbname = properties["baltrad.db.dbname"]
    username = properties["baltrad.db.username"]
    password = properties["baltrad.db.password"]
    
    db = baltrad_database(prefix, propertyfile, hostname, dbname, username, password)
    db.create()

  ##
  # Upgrades the database tables
  #
  def _upgrade_database(self, properties):
    prefix = properties["baltrad.install.root"]
    propertyfile = "%s/etc/bltnode.properties"%prefix
    hostname = properties["baltrad.db.hostname"]
    dbname = properties["baltrad.db.dbname"]
    username = properties["baltrad.db.username"]
    password = properties["baltrad.db.password"]
    
    db = baltrad_database(prefix, propertyfile, hostname, dbname, username, password)
    db.upgrade()
  
  ##
  # Updates the DEX admin users password
  #
  def _update_admin_password(self, properties):
    prefix = properties["baltrad.install.root"]
    propertyfile = "%s/etc/bltnode.properties"%prefix
    hostname = properties["baltrad.db.hostname"]
    dbname = properties["baltrad.db.dbname"]
    username = properties["baltrad.db.username"]
    password = properties["baltrad.db.password"]
    db = baltrad_database(prefix, propertyfile, hostname, dbname, username, password)
    db.update_admin_password(self._password)
  
  ##
  # Creates the bltnode.properties file under the baltrad.install.root/etc/
  # @param properties: the properties to be used
  #
  def _configure_bltnode_properties(self, properties):
    iroot = properties["baltrad.install.root"]
    dbusername=properties["baltrad.db.username"]
    dbpassword=properties["baltrad.db.password"]
    dbhostname=properties["baltrad.db.hostname"]
    dbname=properties["baltrad.db.dbname"]
    nodename=properties["baltrad.node.name"]
    keyczar_root=properties["baltrad.keyczar.root"]
    dex_uri=properties["baltrad.dex.uri"]

    if not os.path.exists("%s/etc"%iroot):
      os.makedirs("%s/etc"%iroot)

    with open("%s/etc/bltnode.properties"%iroot, "w") as fp:
      fp.write("\n#BDB settings\n")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.type", "cherrypy")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.threads", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.backlog", "5")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.cherrypy.timeout", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.uri", "http://localhost:8090")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.type", "sqla")
      fp.write("baltrad.bdb.server.backend.sqla.uri = postgresql://%s:%s@%s/%s\n"%(dbusername,dbpassword,dbhostname,dbname))
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.pool_size", "10")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.log.level", "INFO")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.storage.type", "db")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.storage.fs.path", iroot + "/bdb_storage")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.backend.sqla.storage.fs.layers", "3")
      self._write_property_to_file(fp, properties, "baltrad.bdb.server.auth.providers", "noauth, keyczar")
      fp.write("baltrad.bdb.server.auth.keyczar.keystore_root = %s\n"%keyczar_root)
      fp.write("baltrad.bdb.server.auth.keyczar.keys.%s = %s.pub\n"%(nodename,nodename))
      fp.write("\n# BEAST PGF Specific values\n")
      
      fp.write("baltrad.beast.server.url = %s\n"%dex_uri)
      fp.write("baltrad.beast.pgf.nodename = %s\n"%nodename)
      fp.write("baltrad.beast.pgf.url = http://localhost\n")
      fp.write("baltrad.beast.pgf.key = %s/%s.priv\n"%(keyczar_root,nodename))
      
      fp.write("\n# RAVE PGF Specific values\n")
      fp.write("rave.db.uri=postgresql://%s:%s@%s/%s\n"%(dbusername,dbpassword,dbhostname,dbname))

    fp.close()

  ##
  # Updates the dex.properties file in the BaltradDex tomcat directory (baltrad.install.3p_root/....)
  # @param properties: the properties to be used
  #
  def _configure_dex_properties(self, properties):
    iroot = properties["baltrad.install.3p_root"]
    nodename=properties["baltrad.node.name"]
    keyczar_root=properties["baltrad.keyczar.root"]
    nodeaddress = None
    if "baltrad.node.address" in properties:
      nodeaddress=properties["baltrad.node.address"]

    with open("%s/tomcat/webapps/BaltradDex/dex.properties"%iroot) as fp:
      lines = fp.readlines()
    fp.close()
    (fd, fname) = tempfile.mkstemp()
    fp = os.fdopen(fd, "w")
    for l in lines:
      modline = l
      modline = re.sub("^\s*key.alias\s*=\s*.*","key.alias=%s"%nodename,modline)
      modline = re.sub("^\s*node.name\s*=\s*.*","node.name=%s"%nodename,modline)
      modline = re.sub("^\s*keystore.directory\s*=\s*.*","keystore.directory=%s"%keyczar_root,modline)
      if nodeaddress:
        modline = re.sub("^\s*node.address\s*=\s*.*","node.address=%s"%nodeaddress,modline)
      fp.write("%s"%modline)
    fp.close()

    shutil.move(fname, "%s/tomcat/webapps/BaltradDex/dex.properties"%iroot)

  ##
  # Updates the db.properties file in the BaltradDex tomcat directory (baltrad.install.3p_root/....)
  # @param properties: the properties to be used
  #
  def _configure_dex_db_properties(self, properties):
    iroot = properties["baltrad.install.3p_root"]
    dbusername=properties["baltrad.db.username"]
    dbpassword=properties["baltrad.db.password"]
    dbhostname=properties["baltrad.db.hostname"]
    dbname=properties["baltrad.db.dbname"]
    
    with open("%s/tomcat/webapps/BaltradDex/db.properties"%iroot, "w") as fp:
      fp.write("Autogenerated by post config script\n")
      fp.write("db.jar=postgresql-8.4-701.jdbc4.jar\n")
      fp.write("db.driver=org.postgresql.Driver\n")
      fp.write("db.url=jdbc:postgresql://%s/%s\n"%(dbhostname,dbname))
      fp.write("db.user=%s\n"%dbusername)
      fp.write("db.pwd=%s\n"%dbpassword)
    fp.close()

  ##
  # Updates the dex.fc.properties file in the BaltradDex tomcat directory (baltrad.install.3p_root/....)
  # @param properties: the properties to be used
  #
  def _configure_dex_fc_properties(self, properties):
    tproot = properties["baltrad.install.3p_root"]
    iroot = properties["baltrad.install.root"]
    bdburi = properties["baltrad.bdb.server.uri"]
    storagefolder = "%s/bdb_storage"%iroot
    keyczar_root=properties["baltrad.keyczar.root"]
    nodename=properties["baltrad.node.name"]
    
    with open("%s/tomcat/webapps/BaltradDex/WEB-INF/classes/resources/dex.fc.properties"%tproot, "w") as fp:
      fp.write("#Autogenerated by install script\n")
      fp.write("database.uri=%s\n"%bdburi)
      fp.write("# File catalog data storage directory\n")
      fp.write("data.storage.folder=%s\n"%storagefolder)
      fp.write("# Keyczar key to communicate with node\n")
      fp.write("database.keyczar.key=%s/%s.priv\n"%(keyczar_root, nodename))
      fp.write("# Name of the node\n")
      fp.write("database.keyczar.name=%s\n"%nodename)
      
    fp.close()
  
  ##
  # Updates the rave_defines.py file in the rave directory (baltrad.install.root/rave/Lib/....)
  # @param properties: the properties to be used
  #
  def _configure_rave(self, properties):
    iroot = properties["baltrad.install.root"]
    nodename=properties["baltrad.node.name"]
    keyczar_root=properties["baltrad.keyczar.root"]
    dex_post_uri=properties["baltrad.dex.uri"]
    dex_uri=dex_post_uri.replace("/post_file.htm","")
    
    ct_path = None
    if "rave.ctpath" in properties:
      ct_path=properties["rave.ctpath"]
      
    pgfs = None
    if "rave.pgfs" in properties:
      pgfs=properties["rave.pgfs"]
      
    loglevel = None
    if "rave.loglevel" in properties:
      loglevel=properties["rave.loglevel"]
      
    logid = None
    if "rave.logid" in properties:
      logid=properties["rave.logid"]

    fd = open("%s/rave/Lib/rave_defines.py"%iroot)
    rows = fd.readlines()
    fd.close()
    nrows=[]
    for row in rows:
      if row.startswith("DEX_SPOE"):
        row = "DEX_SPOE = \"%s\"\n"%dex_uri
      elif row.startswith("DEX_NODENAME"):
        row = "DEX_NODENAME = \"%s\"\n"%nodename
      elif row.startswith("DEX_PRIVATEKEY"):
        row = "DEX_PRIVATEKEY = \"%s/%s.priv\"\n"%(keyczar_root,nodename)
      elif row.startswith("BDB_CONFIG_FILE"):
        row = "BDB_CONFIG_FILE = \"%s/etc/bltnode.properties\"\n"%iroot
      elif row.startswith("CTPATH") and ct_path:
        row = "CTPATH = \"%s\"\n"%ct_path
      elif row.startswith("PGFs") and pgfs:
        row = "PGFs = %s\n"%pgfs
      elif row.startswith("LOGLEVEL") and loglevel:
        row = "LOGLEVEL = \"%s\"\n"%loglevel
      elif row.startswith("LOGID") and logid:
        row = "LOGID = 'PGF[%s]'\n"%logid
      nrows.append(row)
    fp = open("%s/rave/Lib/rave_defines.py"%iroot, "w")
    for row in nrows:
      fp.write(row)
    fp.close()


##
# MAIN
if __name__ == "__main__":
  from optparse import OptionParser
  parser = OptionParser(usage = "Usage: %prog [options] [export|setup]",
                        description = """
Utility for configuring a baltrad node post installation. It also provides functionality for
upgrading and installing the baltrad database.

The configuration file is a specific post configuration format but it can 
be generated from a bltnode.properties file by executing the command\n
  
  python bin/baltrad_post_config.py \\ 
    --nodeprops=/opt/baltrad/etc/bltnode.properties \\
    --config=myconfig.properties export

After that you can modify the myconfig.properties file and use that 
one for generating the post configuration.
""")
  parser.add_option("-c", "--config", dest="config",
                  help="Specifies the configuration file to be used for setting up your node (MANDATORY)", 
                  metavar="CONFIG")
  parser.add_option("-n", "--nodeprops", dest="nodeproperties",
                  help="Specifies the bltnode.properties file that was generated during installation", 
                  metavar="NODEPROPERTIES")
  parser.add_option("-p", "--password", dest="password",
                  help="Sets the DEX 'admin' users password. ",
                  metavar="PASSWORD")
  parser.add_option("-u", "--upgrade-database",
                    action="store_true",
                    dest="upgrade_db_flag",
                    default=False,
                    help="Indicate that database should be upgraded.")
  parser.add_option("-i", "--install-database",
                    action="store_true",
                    dest="install_db_flag",
                    default=False,
                    help="Indicate that database should be installed.")
  
  (options,args) = parser.parse_args()
  if not options.config:
    parser.print_help()
    sys.exit(127)
  
  runner = baltrad_post_config(options.config, options.install_db_flag, options.upgrade_db_flag, options.password)
  if "export" in args:
    if not options.nodeproperties:
      print "You must specify --nodeprops=... when exporting the configuration"
      sys.exit(127)
    runner.export(options.nodeproperties)
  elif "setup" in args:
    runner.setup()
