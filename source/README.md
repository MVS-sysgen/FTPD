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
- **build** - contains instructions needed to build the FTPD server automatically and from scratch


## Building from source

To build FTPD from sources (ASM and C) you can follow the instructions in [BUILD.md](build/BUILD.md).



