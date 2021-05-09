# MVS 3.8J FTPD Server

**Note**: This FTP server was originally written by Jason Winter and Juergen Winkelmann.

## Automated Install

If you're using SYSGEN (link) you can run the TSO command: `INSTALL FTPD` this
will automatically install the FTPD server and start the server running on
`localhost:2121`

To enable the FTPD server after IPL run the command `/s ftpd,srvport=2121`

## Building from source

See BUILD.md for instructions how to build from source

## Manual Install

Upload the XMI file `FTPD.xmi` and receive the file with RECV370.

Inside the XMI file is `FTPD`, `FTPDPROC` and `FTPDXCTL`

Before proceeding you need to make changes to RAKF and parmlibs

### RAKF User

You must add the FTPD user and group to RAKF in `SYS1.SECURE.CNTL(USERS)`

:warning: make sure you pick a suitably random password

:warning: RAKF users must be in alphabetical order

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

Copy `SYS1.PARMLIB(VATLST00)` to `SYS1.PARMLIB(VATLSTFF)` and remove and
remove any devices you don't want the FTP deamon to have access to.

e.g.

```
MVSRES,0,2,3350    ,Y        SYSTEM RESIDENCE (PRIVATE)
MVS000,0,2,3350    ,Y        SYSTEM DATASETS (PRIVATE)
PUB000,1,2,3380    ,N        PUBLIC DATASETS (PRIVATE)
PUB001,1,2,3390    ,N        PUBLIC DATASETS (PRIVATE)
SYSCPK,1,2,3350    ,N        COMPILER/TOOLS (PRIVATE)
```

