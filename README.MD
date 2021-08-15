# MVS 3.8J FTPD Server

**Note**: This FTP server was originally written by Jason Winter and Juergen Winkelmann.

This FTP daemon requires RAKF to run. You must install RAKF for this FTP server to work.

## Automated Install

If you're using [MVS/CE](https://github.com/MVS-sysgen/sysgen) This should be already installed.

If you want to reinstall you can run the TSO command: `INSTALL FTPD` this will automatically
install the FTPD server and start the server running on `localhost:2121`

## Access

Using this install everyone in the RAKF group `ADMIN` has access to use FTP. To add users to FTP
add the user or group to `SYS1.SECURE.CNTL(PROFILES)`, the line below allows members of
the `USERS` group to access FTP:

```
FACILITYFTPAUTH                                     USERS   READ
```

:exclamation: RAKF profiles must be in alphabetical order

## Operation

To start the FTPD server after IPL run the command `/s ftpd` in the hercules console. To make changes to the configuration (ports, IP etc)
you can edit the config file `SYS1.PARMLIB(FTPDPM00)`. If you have a custom configuration file you can edit the proc and replace

```
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=8192K
```

with this, adding your own parmlib

```
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=8192K,
//       PARM='PARMLIB=PLACE.WITH.PARMLIBS(FTPPARMS)'
```

To stop the FTP server run the command `/p ftpd` or `/stop ftpd` on the hercules console.

A seperate JCL procedure (`FTPDPARM`) has been made to parse parameters. It takes the following arguments:

- SRVPORT - The port that the FTPD server will listen on.
- SRVIP - The IP address of the hercules host machine to listen on. The default is 'any' which is the equivalent of 'all' or '0.0.0.0'.
- PASVADR - IP address to return for passive mode, comma separated. The default is '127,0,0,1'. This address is used only if getsockname doesn't return a suitable value.
- FAST - When set to `TRUE` Library Optimisation Extensions are enabled
- AUTHUSER - If set, this user can use `quote term`/`quote terminate` to shutdown the FTP server remotely
- DD - The name of a *required* DD name in the JCL. Currently used for an internal reader.

:exclamation: If you're not using MVS/CE you should follow the manual install.

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

Then install the FTPD procedures in `SYS2.PROCLIB`:

#### FTPD

This launches FTPD with the config file located at `SYS1.PARMLIB(FTPDPM00)` (the default). Start with `/s FTPD`.

```jcl
//FTPDPROC EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPD   PROC
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPD to start FTP server
//*
//* To change settings edit config file SYS1.PARMLIB(FTPDPM00)
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='DD=AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
@@
//SYSUT2   DD DISP=SHR,DSN=SYS2.PROCLIB(FTPD)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
```

#### FTPDCONF

This launches FTPD with the config file located at `SYS1.PARMLIB(FTPDPM00)` but can be changed with the `PARMLIB=` agument.
For example you can change the config file use by using `/s FTPDCONF,PARMLIB=SYS2.PARMLIB(FTPDCONF1)`.

```jcl
//FTPDCONF EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPDCONF   PROC PARMLIB='SYS1.PARMLIB(FTPDPM00)'
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC with custom parmlib
//* To use: in Hercules console issue
//*    /s FTPD,parmlib=sys2.parmlib(file)
//* to start FTP server with custom config file
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='PARMLIB=&PARMLIB DD=AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
@@
//SYSUT2   DD DISP=SHR,DSN=SYS2.PROCLIB(FTPDCONF)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
```

#### FTPDPARM

This launches FTPD with but allows the defaults and config file entries for `SRVPORT` and `SRVIP` to be overridden. For example,
`/s ftpdparm,srvport=54321,srvip=10.10.10.10`

```jcl
//FTPDPARM EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPDCONF   PROC SRVPORT='2121',SRVIP='any'
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC with custom arguments
//* To use: in Hercules console issue
//*    /s FTPD,srvport=54321,srvip=10.10.10.10
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='SRVPORT=&SRVPORT SRVIP=&SRVIP DD=AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
@@
//SYSUT2   DD DISP=SHR,DSN=SYS2.PROCLIB(FTPDPARM)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
```

### RAKF User

Before proceeding you need to also make changes to RAKF and parmlibs

You must add the FTPD user and group to RAKF in `SYS1.SECURE.CNTL(USERS)`

:warning: make sure you pick a suitably random password not `RANDOM`

:exclamation: RAKF users must be in alphabetical sort order

```
# User   Group
FTPD     FTPD     RANDOM   N
```

Then update rakf from the hercules console with `/s rakfuser`.

### RAKF Profile

You also need to approve the group FTPD to have access to SVC244 by
adding the following to `SYS1.SECURE.CNTL(PROFILES)`

```
FACILITYSVC244                                      FTPD    READ
```

You also need to add the `FTPAUTH` resource to the facility class. The
lines below block access to anyone not in the ADMIN group.

:exclamation: RAKF profiles must be in alphabetical order (i.e. FTPAUTH should follow DIAG8)

```
FACILITYFTPAUTH                                             NONE
FACILITYFTPAUTH                                     ADMIN   READ
```

Then update rakf from the hercules console with `/s rakfprof`

### SYS1.PARMLIB(FTPDPM00)

Copy the file `FTPD.conf` to `SYS1.PARMLIB(FTPDPM00)`

### Launch FTPD

You're all setup now you can launch FTPD with `/s ftpd,srvport=2121`
