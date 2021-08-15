# FTPD Source Code

These folders contain the source code for the RAKF enabled FTPD server for MVS 3.8j.

## Folders

- **c** - contains the C source for the FTPD server itself
    - ftpd.c - Main FTPD daemon C code
    - mvsdirs.h - functions for managing MVS resources
- **hlasm** - contains the ASM needed to support RAKF
    - FTPDXCTL - Wrapper for FTPD started task to run using user/group FTPD/USER instead of STC/STCGROUP.
    - FTPAUTH - C function to authorize or unauthorize FTPD.
    - FTPSU - C function to switch user.
    - FTPLOGIN - C function to process user login to the FTP service.
    - FTPLGOUT - C function to process FTP user logout.
- **build** - contains instructions needed to build the FTPD server from scratch
- **auto** - contains scripts that can be used to automate the build/release process for FTPD


## Build from source

To build FTPD from sources (ASM and C) you can follow the instructions in [BUILD.md](build/BUILD.md).

## Using Build Automation

:warning: this is experimental :warning:

If you've made changes and wish to build from scratch you can use the script file `build_automation.rc`. To
use it from the hercules console place this repo in the `SYSGEN/SOFTWARE` folder and type: `script ../SOFTWARE/FTPD/source/auto/build_automation.rc`.

This will compile, link, ands generate an XMI file with FTPD and FTPDXCTL located at `SYSGEN.FTPD.XMIT` for release.

If you built FTPD and haven't installed it previously make sure you follow the steps in the README from **RAKF** onward
otherwise you'll get abnormal ends.

