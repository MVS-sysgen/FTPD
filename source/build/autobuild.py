# this code will IPL and generate the object code needed to compile FTPD

from pathlib import Path
import sys
from automvs import automation
import logging
import argparse
import os

cwd = os.getcwd()

install_maclibs = '''//MVPMACLB JOB (FTPD),
//            'Make FTP Daemon',
//            CLASS=A,
//            MSGCLASS=A,
//            REGION=8M,
//            MSGLEVEL=(1,1),
//            USER=IBMUSER,PASSWORD=SYS1
//* The build requires the MACLIB package
//MVPINST EXEC MVP,INSTALL='MACLIB -D' 
'''

desc = 'FTP Autobuild Script'
arg_parser = argparse.ArgumentParser(description=desc)
arg_parser.add_argument('-d', '--debug', help="Print debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
arg_parser.add_argument('-m', '--mvsce', help="MVS/CE folder location", default="MVSCE")
arg_parser.add_argument('--objects',help="Builds HLASM instead of XMI file", action="store_true")
args = arg_parser.parse_args()

builder = automation(mvsce=args.mvsce,loglevel=args.loglevel)
try:
  if args.objects:  
    builder.ipl(clpa=False)
    builder.submit(install_maclibs)
    builder.wait_for_job("MVPMACLB")
    builder.check_maxcc("MVPMACLB")
    builder.send_oper("$s punch1")
    builder.wait_for_string("$HASP000 OK")
    with open("{}/assemble_ftprakf.jcl".format(cwd), "r") as infile:
        builder.submit(infile.read())
    builder.wait_for_string("$HASP190 MAKEFTPD SETUP -- PUNCH1   -- F = STD1")
    builder.send_oper("$s punch1")
    builder.wait_for_string("HASP250 MAKEFTPD IS PURGED")
    builder.check_maxcc("MAKEFTPD")
  else:
    builder.ipl(clpa=False)
    builder.send_oper("$s punch1")
    builder.wait_for_string("$HASP000 OK")
    with open("{}/reader.jcl".format(cwd), "rb") as infile:
      builder.submit(infile.read(),port=3506,ebcdic=True)
    builder.wait_for_string("$HASP190 LINKFTPD SETUP -- PUNCH1   -- F = STD1")
    builder.send_oper("$s punch1")
    builder.wait_for_string("HASP250 LINKFTPD IS PURGED")
    builder.check_maxcc("LINKFTPD")

finally:
    builder.quit_hercules()

with open("punchcards/pch00d.txt", 'rb') as punchfile:
    punchfile.seek(160)
    no_headers = punchfile.read()
    no_footers = no_headers[:-80]

os.chdir(cwd)


if args.objects:  
  with open("ftpdrakf.punch", 'wb') as objects_out:
      objects_out.write(no_footers)
else:
  with open("FTPD.XMI", 'wb') as xmi_out:
      xmi_out.write(no_footers)
      