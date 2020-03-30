#!/usr/bin/env python3
"""KiCad git filters

This program configures a git repo to filter some annoying changes in KiCad
files that doesn't really need to be recorded.
"""
__author__   ='Salvador E. Tropea'
__copyright__='Copyright 2020, INTI'
__credits__  =['Salvador E. Tropea']
__license__  ='GPL 2.0'
__version__  ='1.0.1'
__email__    ='salvador@inti.gob.ar'
__status__   ='beta'

from os.path import (isfile,isdir,basename,sep,dirname,realpath)
from os import (getcwd,remove,rename)
from shutil import (which)
from sys import (exit)
from subprocess import (call)
import argparse
import logging
import re

# Exit error codes
NO_GIT_ROOT=1
MISSING_GIT=2

git_attributes='.gitattributes'
git_config='.gitconfig'

patterns=['*.csv','*.html','*.gbr','*.gbrjob','*.xml','*.kicad_pcb','*.net']
filter_names=['bom_csv','bom_html','gerber','gbrjob','xml','kicad_pcb_f','net_filter']
# Escape sequence nightmare :-(
clean=[r"sed -E 's/^BoM Date:.*$/BoM Date:Date/'",
       r"sed -E 's/^<tr><td>BoM Date<\\/td><td>.*$/<tr><td>BoM Date<\\/td><td>Date<\\/td><\\/tr>/'",
       r"sed -E -e 's/^%TF.CreationDate,.*$/%TF.CreationDate,Date%/' -e 's/^G04 Created by KiCad.*$/G04 Created by KiCad*/'",
       r"sed -E 's/\"CreationDate\":.*/\"CreationDate\":  \"Date\"/'",
       r"sed -E -e 's/^        <date>.*<\\/date>/        <date>Date2<\\/date>/' -e 's/^    <date>.*<\\/date>/    <date>Date1<\\/date>/'",
       r"sed -E 's/\\(host pcbnew ([[:digit:]]+\\.[[:digit:]]+\\.[[:digit:]]+).*/\\(host pcbnew \\1\\)/'",
       r"sed -E -e 's/\\(date \\\".*\\\"\\)/\\(date \\\"Date\\\"\\)/'"]
smudge=[r"sed -E \"s/BoM Date:Date/BoM Date:,`date +\\\"%a %d %b %Y %X %:::z\\\"`/\"",
        r"sed -E \"s/<tr><td>BoM Date<\\/td><td>Date<\\/td><\\/tr>/<tr><td>BoM Date<\\/td><td>`date +\\\"%a %d %b %Y %X %:::z\\\"`<\\/td><\\/tr>/\"",
        r"sed -E \"s/%TF.CreationDate,Date%/%TF.CreationDate,`date +%Y-%m-%dT%H:%M:%S%:z`/\"",
        r"sed -E \"s/\\\"CreationDate\\\":  \\\"Date\\\"/\\\"CreationDate\\\":  \\\"`date +%Y-%m-%dT%H:%M:%S%:z`\\\"/\"",
        r"sed -E -e \"s/<date>Date1<\\/date>/<date>`date +\\\"%a %d %b %Y %X %:::z\\\"`<\\/date>/\" -e \"s/<date>Date2<\\/date>/<date>`date +\\\"%Y-%m-%d\\\"`<\\/date>/\"",
        None,
        r"sed -E -e \"s/\\(date \\\"Date\\\"\\)/\\(date \\\"`date +\\\"%a %d %b %Y %X %:::z\\\"`\\\"\\)/\""]


def add_filter(name, clean, smudge):
    filter = "[filter \"%s\"]\n" % name
    if clean is not None:
        filter = filter + "\tclean = %s\n" % clean
    if smudge is not None:
        filter = filter + "\tsmudge = %s\n" % smudge
    return filter


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='KiCad GIT filters')

    parser.add_argument('--verbose','-v',action='count',default=0)
    parser.add_argument('--version','-V',action='version', version='%(prog)s '+__version__+' - '+
                        __copyright__+' - License: '+__license__)

    args=parser.parse_args()

    # Create a logger with the specified verbosity
    if args.verbose>=2:
       log_level=logging.DEBUG
       verb='-vv'
    elif args.verbose==1:
       log_level=logging.INFO
       verb='-v'
    else:
       verb=None
       log_level=logging.WARNING
    logging.basicConfig(level=log_level)
    logger=logging.getLogger(basename(__file__))

    # Check the environment
    if which('git')==None:
       logger.error('No git command, install it')
       exit(MISSING_GIT)

    # The script must be invoked from the root of the repo
    dir_git=getcwd()+sep+'.git'
    if not isdir(dir_git):
       logger.error('Run this script from the root of your repo (no .git/ here)')
       exit(NO_GIT_ROOT)

    # Configure the repo to use a local .gitconfig file
    logger.info('Configuring git to use ".gitconfig" as a configuration file')
    command=['git','config','--local','include.path','../'+git_config]
    logger.debug(command)
    call(command)

    # Edit the attributes file
    if not isfile(git_attributes):
       # New file
       logger.info('Creating '+git_attributes)
       attr_file=open(git_attributes,"w+")
       for i in range(0,len(patterns)):
           attr_file.write("%s filter=%s\n" % (patterns[i],filter_names[i]))
           logger.debug('Adding filter %s for %s' % (filter_names[i],patterns[i]))
       attr_file.close()
    else:
       # Already existing
       logger.info('A '+git_attributes+' file already exists')
       old_file=open(git_attributes,"r")
       new_file=open(git_attributes+'.tmp',"w+")
       for line in old_file:
           z=re.match('(\S+)\s+filter=(\S+)',line)
           if z:
              res=z.groups()
              if not(res[0] in patterns):
                 # Copy other filters
                 new_file.write("%s filter=%s\n" % (res[0],res[1]))
           else:
              # Copy anything that isn't a filter
              new_file.write(line)
       old_file.close()
       # Add our filters
       for i in range(0,len(patterns)):
           new_file.write("%s filter=%s\n" % (patterns[i],filter_names[i]))
           logger.debug('Adding filter %s for %s' % (filter_names[i],patterns[i]))
       new_file.close()
       remove(git_attributes)
       rename(git_attributes+'.tmp',git_attributes)

    # Edit the config file
    if not isfile(git_config):
       # New file
       logger.info('Creating '+git_config)
       cfg_file=open(git_config,"w+")
       for i in range(0,len(patterns)):
           cfg_file.write(add_filter(filter_names[i],clean[i],smudge[i]))
           logger.debug('Adding filter %s' % filter_names[i])
       cfg_file.close()
    else:
       # Already existing
       logger.info('A '+git_config+' file already exists')
       old_file=open(git_config,"r")
       new_file=open(git_config+'.tmp',"w+")
       do_skip=False
       for line in old_file:
           # Is the begining of a filter?
           z=re.match('\[filter\s+\"(\S+)\"\]',line)
           if z:
              # Yes
              res=z.groups()
              logger.debug('Found filter '+res[0])
              # Is one of our filters?
              if not(res[0] in filter_names):
                 # Copy other filters
                 new_file.write("[filter \"%s\"]\n" % res[0])
                 do_skip=False
              else:
                 # Skip our filters, will add at the end
                 do_skip=True
           else:
              if line[0].isspace():
                 # Content of a section
                 if not do_skip:
                    new_file.write(line)
              else:
                 # Starting another kind of section
                 do_skip=False
                 new_file.write(line)
       old_file.close()
       # Add our filters
       for i in range(0,len(patterns)):
           new_file.write(add_filter(filter_names[i],clean[i],smudge[i]))
           logger.debug('Adding filter %s' % filter_names[i])
       new_file.close()
       remove(git_config)
       rename(git_config+'.tmp',git_config)



