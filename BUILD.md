# Building from source:

### Before You Start

**Make sure you're running the latest SDL Hyperion and have enabled `HERC_TCPIP_EXTENSION` and `HERC_TCPIP_PROB_STATE` *before* you IPL**

Place the following at the top of an RC file and launch hercules with: `hercules -r tcpip.rc`

```
facility enable HERC_TCPIP_EXTENSION
facility enable HERC_TCPIP_PROB_STATE
```

If you are using MVS/CE building requires the MACLIBS package. Install with the TSO command `INSTALL MACLIBS`.

## Using Build Automation

If you've made changes and wish to build from scratch you can use the script file `build_automation.rc`. To
use it from the hercules console place this repo in the `SYSGEN/SOFTWARE` folder and type: `script ../SOFTWARE/FTPD/build_automation.rc`.

This script does all the steps outlined below as well as generating an XMI file with FTPD and FTPDXCTL located
at `SYSGEN.FTPD.XMIT`.

If you built FTPD and haven't installed it previously make sure you follow the steps in the README from **RAKF** onward
otherwise you'll get abnormal ends.

### Compiling FTP


### Building From Scratch


1) Get JCC: `git clone https://github.com/mvslovers/jcc.git`
1) Get rdrprep: `git clone https://github.com/mvslovers/rdrprep.git`
  - Install rdrprep with `make` and `sudo make install`
1) Generate new JCL to assemble the FTP hlasm programs:`rdrprep --print build_01_assemble_ftp_objects.template |grep -v getASCIIline > 01_assemble_ftp_objects.jcl`
1) Change the punch output file and folder by type the following on the hercules console `detach d` followed by `attach d 3525 ../SOFTWARE/FTPD/ftpdrakf.punch ebcdic`
1) Then submit `01_assemble_ftp_objects.jcl` to the socket reader `../sysgen/submit.sh 01_assemble_ftp_objects.jcl`
  - When you see `/ $HASP150 MAKEFTPD ON PUNCH1          34 CARDS` in the hercules console type: `/$s punch1`, this will place the assembled binary in `../SOFTWARE/FTPD/ftpdrakf.punch`
1) Remove  ftpdrakf.punch header and footer with linux command: `dd if=ftpdrakf.punch bs=1 skip=160 count=2720 of=ftpdrac.pch`
1) Use `objscan` from jcc to replace HLASM names: `~/jcc/objscan ftpdrac.pch objscan_input.nam ftpdrac.obj`
  - This command replaced the labels/names in HLASM like `FTPLOGIN` with `rac_user_login` which is used in `ftpd.c`
  - This step creates `ftpdrac.obj`
1) Compile `ftpd.c` with jcc: `~/jcc/jcc -I/path/to/jcc/include -I./ -D__MVS_ -o -list=list.out ftpd.c`
  - This will create `ftpd.obj`
1) Use `prelink` to link the object: `./jcc/prelink -r jcc/objs ftpd.load ftpd.obj ftpdrac.obj`
  - This creates `ftpd.load` which is our assembled program ready to link in MVS
1) This step is complicated but first you create the JCL in EBCDIC, then then submit the job to the reader on port 3506 which speaks ebcdic:
1) Generate an EBCDIC JCL with the `ftpd.load` inside: `rdrprep build_03_link_ftpd.template`
1) Submit this job which will link and place `FTPD` in `SYS2.LINKLIB`: `cat reader.jcl | ncat --send-only -w1 localhost 3506 `

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
