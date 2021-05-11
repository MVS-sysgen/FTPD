# Building from source:

### Before You Start

**Make sure you're running the latest SDL Hyperion and have enabled `HERC_TCPIP_EXTENSION` and `HERC_TCPIP_PROB_STATE` *before* you IPL**

Place the following at the top of an RC file and launch hercules with: `hercules -r tcpip.rc`

```
facility enable HERC_TCPIP_EXTENSION
facility enable HERC_TCPIP_PROB_STATE
```

## Using Build Automation

If you've made changes and wish to build from scratch you can use the script file `build_automation.rc`. To
use it from the hercules console use: `script ../SOFTWARE/FTPD/build_automation.rc`.

This script does all the steps outlined below as well as generating an XMI file with FTPD and FTPDXCTL located
at `SYSGEN.FTPD.XMIT`.

If you built FTPD and haven't installed it previously make sure you follow the steps in the README from **RAKF** onward
otherwise you'll get abnormal ends.

### Compiling FTP

If you only make changes to `ftpd.c`/`mvsdirs.h` then follow these steps:

1) Compile `ftpd.c` with jcc: `~/jcc/jcc -I/path/to/jcc/include -I./ -D__MVS_ -o -list=list.out ftpd.c`
  - This will create `ftpd.obj`
2) Use `objscan` from jcc to replace HLASM names: `~/jcc/objscan FTPOBJ objscan_input.nam ftpdrac.obj`
  - This creates `ftpdrac.obj`
3) Use `prelink` to link the object: `./jcc/prelink -r jcc/objs output.load ftpd.obj ftpdrac.obj`
  - This creates `output.load`
4) This step is complicated but first you create the JCL in EBCDIC, then change the socket reader in hercules to ebcdic, then submit the job:
  - Create the ebcdic jcl file: `rdrprep 03_link_ftpd.template` this will make the file `reader.jcl`
  - Then in the hercules console type the followin two commands: `detach c` and `attach c 3505 3505 sockdev ebcdic trunc eof`
  - Now submit `reader.jcl` with your socket submit script: `../sysgen/submit.sh reader.jcl`


### Building From Scratch

:warning: You must have FTP or IND$FILE installed

*If you made changes to just `ftpd.c`/`mvsdirs.h` you can skip steps 1 through 4*

1) Get JCC: `git clone https://github.com/mvslovers/jcc.git`
2) Get rdrprep: `git clone https://github.com/mvslovers/rdrprep.git`
  - Install rdrprep with `make` and `sudo make install`
3) Generate new JCL to assemble the FTP hlasm programs:`rdrprep --print 01_assemble_ftp_objects.template |grep -v getASCIIline > 01_assemble_ftp_objects.jcl`
4) Then submit `01_assemble_ftp_objects.jcl` to the socket reader `../sysgen/submit.sh 01_assemble_ftp_objects.jcl`
5) Download the file `IBMUSER.FTPOBJ` in :warning:**binary**:warning: to this folder and name it `FTPOBJ`
  - You can use with `IND$FILE` or use the FTP server if you've alread installed it once
6) Compile `ftpd.c` with jcc: `~/jcc/jcc -I/path/to/jcc/include -I./ -D__MVS_ -o -list=list.out ftpd.c`
  - This will create `ftpd.obj`
7) Use `objscan` from jcc to replace HLASM names: `~/jcc/objscan FTPOBJ objscan_input.nam ftpdrac.obj`
  - This creates `ftpdrac.obj`
8) Use `prelink` to link the object: `./jcc/prelink -r jcc/objs output.load ftpd.obj ftpdrac.obj`
  - This creates `output.load`
9) This step is complicated but first you create the JCL in EBCDIC, then change the socket reader in hercules to ebcdic, then submit the job:
  - Create the ebcdic jcl file: `rdrprep 03_link_ftpd.template` this will make the file `reader.jcl`
  - Then in the hercules console type the followin two commands: `detach c` and `attach c 3505 3505 sockdev ebcdic trunc eof`
  - Now submit `reader.jcl` with your socket submit script: `../sysgen/submit.sh reader.jcl`

### Launching FTPD

You can now launch FTPD with this following proc installed in `sys2.proclib` with issuing `/s ftpddev`:

```jcl
//FTPDDEV   PROC PASVADR='127,0,0,1',SRVIP='any',SRVPORT=2121
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPDDEV to start FTP server
//*         on port 2121
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='&PASVADR &SRVPORT &SRVIP //DDN:AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
```