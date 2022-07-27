# Building from source:

## Automated Build

To make building easier and automated the script `autobuild.py` was developed. 
It relies on the python automvs library. A docker build file has been created
which automates all the steps below. 

To use it you can run the following commands from the root folder of this repo:

1) First build the FTPD XMI and install files: `docker build --tag ftpd:builder .`
2) Then mount the local folder inside the docker container: `docker run -it --entrypoint /bin/bash -v $(pwd):/project mainframed767/ftpd:builder`
3) Once inside the container copy the files to `/project`: `cp * /project`

## Before You Start

:warning: Shell commands should all be run from withing the `FTPD/source/build/` folder.

### Enable TCPIP

**Make sure you're running the latest SDL Hyperion and have enabled `HERC_TCPIP_EXTENSION` and `HERC_TCPIP_PROB_STATE` *before* you IPL**

Place the following at the top of an RC file and launch hercules with: `hercules -r tcpip.rc`

```
facility enable HERC_TCPIP_EXTENSION
facility enable HERC_TCPIP_PROB_STATE
```

Note: You do not need to do this if you are running MVS/CE.

### Install required MACLIBS

If you are using MVS/CE building requires the MACLIBS package. Install with the TSO command `RX MVP INSTALL MACLIBS`.

### Installing rdrprep and JCC
1) Get JCC: `git clone https://github.com/mvslovers/jcc.git`
2) Get rdrprep: `git clone https://github.com/mvslovers/rdrprep.git`
    - Install rdrprep with `make` and `sudo make install`

## Compiling FTP

1) Generate new JCL to assemble the FTP hlasm programs:`python3 generate_ftpdrakf.py ../hlasm`
    - This will generate the file `assemble_ftprakf.jcl` which assembles all asm programs in [hlasm](../hlasm)
    - When we submit this job we it will output to the punch card writer
    - This step also assembles **FTPDXCTL** and places it in `SYS2.LINKLIB`
2) Change the punch output file and folder by typing the following on the hercules console `detach d` and enter followed by `attach d 3525 /path/to/FTPD/source/build/ftpdrakf.punch ebcdic`
3) Then submit `assemble_ftprakf.jcl` to the socket reader `cat assemble_ftprakf.jcl | ncat --send-only -w1 127.0.0.1 3505`
    - Each step should complete with `00000`.
    - When you see `/ $HASP150 MAKEFTPD ON PUNCH1          34 CARDS` in the hercules console type: `/$s punch1`, this will place the assembled binary in `/path/to/FTPD/source/build/ftpdrakf.punch`
4) Detach the punch card now in the hercules console: `detach d`
5) The punch writter as configured adds a seperator to the beginning and ends of files. To remove the `ftpdrakf.punch` header and footer you can use either of the following linux commands:
    - `dd if=ftpdrakf.punch bs=1 skip=160 count=2720 of=ftpdrac.pch` (where `count=` is the size of `ftpdrakf.punch` in bytes minus 240)
    - `tail -c +161 ftpdrakf.punch |head -c -80 > ftpdrac.pch`
6) Use `objscan` from jcc to replace HLASM names: `./jcc/objscan ftpdrakf.punch objscan_input.nam ftpdrac.obj`
    - This command replaced the labels/names in ASM like `FTPLOGIN` with `rac_user_login` which is used in `ftpd.c`
    - This step creates `ftpdrac.obj`
7) Compile `ftpd.c` with jcc: `./jcc/jcc -I./jcc/include -I../c -D__MVS_ -o -list=list.out ../c/ftpd.c`
    - It should complete with `JCC-RC:0`
    - This will create the file `ftpd.obj`
    - :exclamation: To enable debug output (which prints to SYSTOUT) add `-D__DEBUG__` to the command above after `-D__MVS_`
8) Use `prelink` to link the object: `./jcc/prelink -r jcc/objs ftpd.load ftpd.obj ftpdrac.obj`
    - It should completed with `PLK-RC:0`
    - This creates `ftpd.load` which is our assembled program ready to link in MVS
9) Generate an EBCDIC JCL file with the `ftpd.load` inside: `rdrprep link_ftpd.template`
    - This will create the file `reader.jcl`
10) Submit this job which will link and place `FTPD` in `SYS2.LINKLIB`: `cat reader.jcl | ncat --send-only -w1 localhost 3506`
    - The `LINKFTPD` step should complete with `00000`.
11) Generate and submit the install JCL which finalizes the install: `python3 generate_install.py ../../FTPD.conf && cat install.jcl | ncat --send-only -w1 127.0.0.1 3505`
    - You should only do this last step once, you wont need to do it again

Congratulations, you compiled FTPD from scratch!

Going forward if you only edit `ftpd.c`/`mvsdirs.h` you only need to do the **bottom 4 steps**!

### Launching FTPD

Place the following JCL in `SYS2.PROCLIB(FTDDEV)` and run from the hercules console with `/s ftpddev` (it can be stopped with `/p ftpddev`):

```jcl
//FTPDDEV   PROC
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPDDEV to start FTP server
//*         on the port configure in SYS1.PARMLIB(FTPDPM00)
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=8192K,
// PARM='DD=AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
```
