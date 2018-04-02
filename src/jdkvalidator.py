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

Validates the jdk and that it supports appropriate data model.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-02-07
'''
from ValidatorException import ValidatorException
import subprocess, os
import re, platform

##
# JDK Validator, tests for JDKHOME, version and if 32 or 64 bit model is supported
#
class jdkvalidator:
  ##
  # Default constructor
  def __init__(self):
    pass
  
  ##
  # Tries to find a suitable jdkhome in the path
  # @return: found system jdk
  # @raise ValidatorException: If it failed to locate a jdk
  # 
  def _identify_system_jdk(self):
    whichjava = subprocess.Popen(['which', 'java'], stdout=subprocess.PIPE).communicate()[0]
    whichjavac = subprocess.Popen(['which', 'javac'], stdout=subprocess.PIPE).communicate()[0]
    
    if whichjava == "" or whichjavac == "":
      raise ValidatorException("Could not find java or javac")
    
    if os.path.dirname(whichjava) != os.path.dirname(whichjavac):
      raise ValidatorException("java and javac are found at different places")
    
    
    jdkhome = os.path.dirname(whichjava)
    if os.path.basename(jdkhome) == "bin":
      jdkhome = os.path.dirname(jdkhome)
    
    return jdkhome
  
  ##
  # Verifies that the java version is >= 1.6
  # @param env: the build environment
  # @return: the version string
  # @raise ValidatorException: on failure
  # 
  def _validate_java_version(self, env):
    javacmd = env.expandArgs("$JDKHOME/bin/java")
    result = subprocess.Popen([javacmd, '-version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]

    lines = result.decode('utf-8').split("\n")
    verstr = None
    for l in lines:
      if l.startswith("java version") or l.startswith("openjdk version"):
        verstr = l
        break
    if verstr == None:
      raise ValidatorException("Could not identify any type of version for java")
      
    g = re.search("(java version \")([0-9._\-]+)(\")", verstr)
    if g == None:
      g = re.search("(openjdk version \")([0-9._\-a-z]+)(\")", verstr)

    if g == None:
      raise ValidatorException("Could not determine version for java")
    
    ver = g.group(2)

    values = ver.split(".")
    
    if int(values[0]) <= 1 and int(values[1]) < 6:
      raise ValidatorException("Java must be SUN or OpenJDK with version >= 1.6")
    
    env.addArg("JAVA_VERSION", ver)
  
    return ver
  
  ##
  # Removes the list of files
  # @param files. a list of files
  #
  def _remove_files(self, files):
    for f in files:
      try:
        os.unlink(f)
      except:
        pass

  ##
  # Tests the supported java datamodel for the provided jdk java
  # @param env: the build environment
  # @return: the supported data model, first by matching data model with machine type and then if model is supported
  #
  def _test_java_datamodel_type(self, env):
    javacmd = env.expandArgs("$JDKHOME/bin/java")
    javaccmd = env.expandArgs("$JDKHOME/bin/javac")
    
    progstr="""
public class TestJava {
  public static void main(String[] args) {
  }
}
"""
    self._remove_files(["TestJava.java","TestJava.class"])

    fp = open("TestJava.java", "w")
    fp.write(progstr)
    fp.close()
    
    code = subprocess.call("%s TestJava.java"%javaccmd, shell=True)
    if code != 0:
      self._remove_files(["TestJava.java","TestJava.class"])
      raise ValidatorException("Failed to compile java test program")
    
    datamodel32 = False
    datamodel64 = False

    code = subprocess.call("%s -d64 TestJava"%javacmd, shell=True)
    if code == 0:
      datamodel64 = True
    
    code = subprocess.call("%s TestJava"%javacmd, shell=True)
    if code == 0:
      datamodel32 = True

    self._remove_files(["TestJava.java","TestJava.class"])
    
    arch_bits = platform.architecture()[0]
    if arch_bits == "64bit" and datamodel64 == True:
      return "64"
    elif arch_bits == "32bit" and datamodel32 == True:
      return "32"
    else:
      raise ValidatorException("Incompatible jvm and platform, arch and jvm differs between 32 and 64 bit models")
    
  ##
  # Performs the actual validation of a jdk
  # @param env: the build environment
  #
  def validate(self, env):
    jdkhome = None
    if env.hasArg("JDKHOME"):
      jdkhome = env.getArg("JDKHOME")
    else:
      jdkhome = self._identify_system_jdk()
      env.addArg("JDKHOME", jdkhome)

    version = self._validate_java_version(env)

    dmodel = self._test_java_datamodel_type(env)
    
    print("Java: %s supports %s-bit data models"%(version,dmodel))
