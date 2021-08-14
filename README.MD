# MVS 3.8J FTPD Server

**Note**: This FTP server was originally written by Jason Winter and Juergen Winkelmann.

This FTP daemon requires RAKF to run. You must install RAKF for this FTP server to work.

## Automated Install

<<<<<<< Updated upstream
If you're using [SYSGEN](https://github.com/MVS-sysgen/sysgen) but are running the verson without software installed you can run the TSO command: `INSTALL FTPD` this will automatically install the FTPD server and start the server running on `localhost:2121`. Otherwise its likely already installed, check in `SYS2.PROCLIB` for `FTPD`. 

## Starting the FTP server
=======
If you're using [MVS/CE](https://github.com/MVS-sysgen/sysgen) you can run the TSO command: `INSTALL FTPD` this
will automatically install the FTPD server and start the server running on
`localhost:2121`
>>>>>>> Stashed changes

To enable the FTPD server after IPL run the command `/s ftpd,srvport=2121`

:warning: If you're not using SYSGEN you should follow the manual install

## Building from source

See BUILD.md for instructions how to build from source.

## Manual Installation

### Uploading/Installing needed files

Upload the XMI file `FTPD.xmi` and receive the file with RECV370 (modify the JCL as needed).

```jcl
//RECVFTPD JOB (TSO),'Recieve XMI',CLASS=A,MSGCLASS=A
//* RECV370 DDNAMEs:
//* ----------------
//*
//*     RECVLOG    RECV370 output messages (required)
//*
//*     RECVDBUG   Optional, specifies debugging options.
//*
//*     XMITIN     input XMIT file to be received (required)
//*
//*     SYSPRINT   IEBCOPY output messages (required for DSORG=PO
//*                input datasets on SYSUT1)
//*
//*     SYSUT1     Work dataset for IEBCOPY (not needed for sequential
//*                XMITs; required for partitioned XMITs)
//*
//*     SYSUT2     Output dataset - sequential or partitioned
//*
//*     SYSIN      IEBCOPY input dataset (required for DSORG=PO XMITs)
//*                A DUMMY dataset.
//*
//RECV370 EXEC PGM=RECV370
//STEPLIB  DD  DISP=SHR,DSN=SYSC.LINKLIB
//* Change DSN to match where you uploaded the file
//XMITIN   DD  DISP=SHR,DSN=USERNAME.FTPDLOAD.XMI
//RECVLOG  DD  SYSOUT=*
//SYSPRINT DD  SYSOUT=*
//SYSIN    DD  DUMMY
//* Work temp dataset
//SYSUT1   DD  DSN=&&SYSUT1,
//             UNIT=VIO,
//             SPACE=(CYL,(5,1)),
//             DISP=(NEW,DELETE,DELETE)
//* Output dataset
//SYSUT2   DD  DSN=SYSGEN.FTPD.LOADLIB,
//             UNIT=SYSALLDA,VOL=SER=PUB001,
//             SPACE=(CYL,(15,2,20),RLSE),
//             DISP=(NEW,CATLG,DELETE)
```

Inside the XMI file is `FTPD`, and `FTPDXCTL`, you need to copy them to your
link library (most likely `SYS2.LINKLIB`):

```jcl
//FTPXMIT1 JOB (TSO),'Recieve XMI',CLASS=A,MSGCLASS=A
//STEP2CPY EXEC PGM=IEBCOPY
//SYSPRINT DD  SYSOUT=*
//* Make sure the SYSUT2 DSN matches where you
//* receive the XMI file above
//SYSUT1   DD  DSN=SYSGEN.FTPD.LOADLIB,DISP=SHR
//SYSUT2   DD  DSN=SYS2.LINKLIB,DISP=SHR
//SYSIN    DD  *
  COPY INDD=((SYSUT1,R)),OUTDD=SYSUT2
```

Then install the `FTPD_PROC.jcl` procedure in `SYS2.PROCLIB`:

```jcl
//FTPDDEVC EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPD   PROC PASVADR='127,0,0,1',SRVIP='any',SRVPORT=21021
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPD to start FTP server on
//*         on port 21021
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='&PASVADR &SRVPORT &SRVIP //DDN:AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
@@
//SYSUT2   DD DISP=SHR,DSN=SYS2.PROCLIB(FTPD)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
```

Before proceeding you need to also make changes to RAKF and parmlibs

### RAKF User

You must add the FTPD user and group to RAKF in `SYS1.SECURE.CNTL(USERS)`

:warning: make sure you pick a suitably random password no `RANDOM`

:warning: RAKF users must be in alphabetical sort order

```
# User   Group
FTPD     FTPD     RANDOM   N
```

Then update rakf from the console with `/s rakfuser`.

### RAKF Profile

You also need to approve the group FTPD to have access to SVC244 by
adding the following to `SYS1.SECURE.CNTL(PROFILES)`

```
FACILITYSVC244                                      FTPD    READ
```

:warning: RAKF profiles must be in alphabetical order (i.e. FTPD should follow ADMIN)

Then update rakf from the console with `/s rakfprof`

### SYS1.PARMLIB(VATLSTFF)

Copy `SYS1.PARMLIB(VATLST00)` to `SYS1.PARMLIB(VATLSTFF)` and
remove any devices you don't want the FTP deamon to have access to.

For example:

```
MVSRES,0,2,3350    ,Y        SYSTEM RESIDENCE (PRIVATE)
MVS000,0,2,3350    ,Y        SYSTEM DATASETS (PRIVATE)
PUB000,1,2,3380    ,N        PUBLIC DATASETS (PRIVATE)
PUB001,1,2,3390    ,N        PUBLIC DATASETS (PRIVATE)
SYSCPK,1,2,3350    ,N        COMPILER/TOOLS (PRIVATE)
```

### Launch FTPD

You're all setup now you can launch FTPD with `/s ftpd,srvport=2121`
