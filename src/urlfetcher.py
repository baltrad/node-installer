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

Fetcher class for fetching files from an http server or similar.

@file
@author Anders Henja (Swedish Meteorological and Hydrological Institute, SMHI)
@date 2011-01-20
'''
import urllib
import os
from fetcher import fetcher

##
# Handle missing files that causes 404 errors
#
class FileURLopener(urllib.FancyURLopener):
  ##
  # Constructor
  # @param args: See FancyURLopener.__init__
  #
  def __init__(self, *args):
    urllib.FancyURLopener.__init__(self, *args)
   
  ##
  # Handles http error code 404                                
  def http_error_default(self, url, fp, errcode, errmsg, headers):
    if errcode == 404:
      raise IOError, "Could not retrieve resource %s"%url

##
# Make sure our opener is used
#
urllib._urlopener = FileURLopener()

##
# The url fetcher class
class urlfetcher(fetcher):
  url = None
  fname = None
  
  ##
  ## http://git.baltrad.eu/blt_dependencies/ 
  ##
  
  ##
  # Constructor
  # @param url: the url to the file to be fetched
  #
  def __init__(self, url):
    super(urlfetcher, self).__init__()
    self.fname = os.path.basename(url)
    self.url = url
  
  ##
  # Fetches the file
  # @param env: the build environment
  # @return the name of the file that was fetched
  #
  def dofetch(self, env=None):
    if not os.path.exists(self.fname):
      urllib.urlretrieve(self.url, self.fname)
    else:
      print "%s already fetched"%self.fname
    return self.fname
  
  ##
  # Removes the file
  # @param env: the build environment
  #
  def doclean(self, env=None):
    if os.path.exists(self.fname):
      os.remove(self.fname)
