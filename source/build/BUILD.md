# Building from source:

## Before You Start

**Make sure you're running the latest SDL Hyperion and have enabled `HERC_TCPIP_EXTENSION` and `HERC_TCPIP_PROB_STATE` *before* you IPL**

Place the following at the top of an RC file and launch hercules with: `hercules -r tcpip.rc`

```
facility enable HERC_TCPIP_EXTENSION
facility enable HERC_TCPIP_PROB_STATE
```

If you are using MVS/CE building requires the MACLIBS package. Install with the TSO command `INSTALL MACLIBS`.

### Compiling FTP

Shell commands should all be run from withing the `FTPD/source/build/` folder.


1) Get JCC: `git clone https://github.com/mvslovers/jcc.git`
1) Get rdrprep: `git clone https://github.com/mvslovers/rdrprep.git`
  - Install rdrprep with `make` and `sudo make install`
1) Generate new JCL to assemble the FTP hlasm programs:`rdrprep --print 01_ftprakf_asm.template |grep -v getASCIIline > 01_ftprakf_asm.jcl`
  - This will generate the file `01_ftprakf_asm.jcl` which assembles four asm programs in [hlasm](../hlasm)
1) Change the punch output file and folder by typing the following on the hercules console `detach d` followed by `attach d 3525 ../SOFTWARE/FTPD/source/build/ftpdrakf.punch ebcdic`
  - When we submit the job we just generated
1) Then submit `01_assemble_ftp_objects.jcl` to the socket reader `cat 01_ftprakf_asm.jcl | ncat --send-only -w1 plex.local 3505`
  - Each step should complete with `00000`.
  - When you see `/ $HASP150 MAKEFTPD ON PUNCH1          34 CARDS` in the hercules console type: `/$s punch1`, this will place the assembled binary in `../SOFTWARE/FTPD/ftpdrakf.punch`
1) Detach the punch card now in the hercules console: `detach d`
1) The punch writter adds spacers to the beginning and ends of files. To remove the `ftpdrakf.punch` header and footer you can use either of the following linux commands:
  - `dd if=ftpdrakf.punch bs=1 skip=160 count=2720 of=ftpdrac.pch` (where `count=` is the size of `ftpdrakf.punch` in bytes minus 240)
  - `tail -c +161 ftpdrakf.punch |head -c -80 > ftpdrac.pch`
1) Use `objscan` from jcc to replace HLASM names: `./jcc/objscan ftpdrac.pch objscan_input.nam ftpdrac.obj`
  - This command replaced the labels/names in ASM like `FTPLOGIN` with `rac_user_login` which is used in `ftpd.c`
  - This step creates `ftpdrac.obj`
1) Compile `ftpd.c` with jcc: `./jcc/jcc -I./jcc/include -I../c -D__MVS_ -o -list=list.out ../c/ftpd.c`
  - It should complete with `JCC-RC:0`
  - This will create the file `ftpd.obj`
1) Use `prelink` to link the object: `./jcc/prelink -r jcc/objs ftpd.load ftpd.obj ftpdrac.obj`
  - It should completed with `PLK-RC:0`
  - This creates `ftpd.load` which is our assembled program ready to link in MVS
1) Generate an EBCDIC JCL file with the `ftpd.load` inside: `rdrprep 02_link_ftpd.template`
  - This will create the file `reader.jcl`
1) Submit this job which will link and place `FTPD` in `SYS2.LINKLIB`: `cat reader.jcl | ncat --send-only -w1 localhost 3506`
  - The `LINKFTPD` step should complete with `00000`.

Congratulations, you compiled FTPD from scratch!

Going forward if you only edit `ftpd.c`/`mvsdirs.h` you only need to do the **bottom 4 steps**!

### Launching FTPD

You can now launch FTPD with this simple proc place in `SYS2.PROCLIB`:

```jcl
//FTPDDEV   PROC
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPDDEV to start FTP server
//*         on port 2121
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=8192K,
// PARM='DD=AAINTRDR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
```
