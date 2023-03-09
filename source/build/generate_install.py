# generates the JCL needed to build the HLASM files

import sys
import random
import string

if len(sys.argv) == 1:
    print("usage: {} /path/to/FTPD.conf".format(sys.argv[0]))
    sys.exit(-1)

def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


install_jcl = '''//#001JCL JOB (FTPD),
//            'FTPD INSTALL',
//            CLASS=A,
//            MSGCLASS=A,
//            REGION=8M,
//            MSGLEVEL=(1,1)
//*
//* Installs FTPD/FTPDXCTL to SYS2.LINKLIB
//* Adds FTPDPM00 to SYS1.PARMLIB
//* Adds FTPD procedure to SYS2.PROCLIB
//* Adds the FTP user and updates RAKF profiles
//*
//FTDELETE EXEC PGM=IDCAMS,REGION=1024K
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
 DELETE SYSGEN.FTPD.LOADLIB NONVSAM SCRATCH PURGE
 DELETE SYS2.PROCLIB(FTPD)
 DELETE SYS2.LINKLIB(FTPD)
 DELETE SYS2.LINKLIB(FTPDXCTL)
 /* IF THERE WAS NO DATASET TO DELETE, RESET CC           */
 IF LASTCC = 8 THEN
   DO
       SET LASTCC = 0
       SET MAXCC = 0
   END
/*
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
//XMITIN   DD  DSN=MVP.WORK(FTPD),DISP=SHR
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
//*
//* Copy FTPD/FTPDXCTL to SYS2.LINKLIB
//*
//STEP2CPY EXEC PGM=IEBCOPY
//SYSPRINT DD  SYSOUT=*
//SYSUT1   DD  DSN=SYSGEN.FTPD.LOADLIB,DISP=SHR
//SYSUT2   DD  DSN=SYS2.LINKLIB,DISP=SHR
//SYSIN    DD  *
  COPY INDD=((SYSUT1,R)),OUTDD=SYSUT2
/*
//*
//* Add FTPD to SYS2.PROCLIB
//*
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
//* Adds FTPDPARM
//FTPDPARM EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPDPARM PROC SRVPORT='2121',AUTHUSR='IBMUSER'
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC with custom arguments
//* To use: in Hercules console issue
//*    /s FTPDPARM,srvport=54321,srvip=10.10.10.10
//*
//********************************************************************
//FTPD   EXEC PGM=FTPDXCTL,TIME=1440,REGION=4096K,
// PARM='SRVPORT=&SRVPORT DD=AAINTRDR AUTHUSR=&AUTHUSR'
//AAINTRDR DD SYSOUT=(A,INTRDR),DCB=(RECFM=FB,LRECL=80,BLKSIZE=80)
//STDOUT   DD SYSOUT=*
@@
//SYSUT2   DD DISP=SHR,DSN=SYS2.PROCLIB(FTPDPARM)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//*
//* Add FTPDPM00 to SYS1.PARMLIB
//*
//FTPDDEVC EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
{ftpd_conf}
@@
//SYSUT2   DD DISP=SHR,DSN=SYS1.PARMLIB(FTPDPM00)
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//ADDRAKFR EXEC PGM=IEBGENER
//SYSPRINT DD SYSOUT=*
//SYSIN DD DUMMY
//SYSUT1    DD *
 /* RAKF REXX SCRIPT ADD FTPD USER AND FACILITY */

call wto "FTPD Install: Adding FTPD user to RAKF"

"ALLOC FI(USERS) DA('SYS1.SECURE.CNTL(USERS)') SHR "
"EXECIO * DISKR USERS (FINIS STEM sortin."

if rc > 0 then do
    say "Error reading SYS1.SECURE.CNTL(USERS):" rc
    "FREE F(USERS)"
    exit 8
end

not_already_installed = 1
do i = 1 to sortin.0
    if pos('FTPD', sortin.i) > 0 then not_already_installed = 0
end

if not_already_installed then do
    call wto "FTPD Install: Creating new string"
    x = sortin.0 + 1
    user_group = LEFT("FTPD",9)||LEFT("FTPD",9)
    sortin.x = user_group||RANDOMPW(5)||" N"
    sortin.0 = x
    call wto "FTPD Install: Sorting"
    CALL RXSORT
    call wto "FTPD Install: writting to disk"
    "EXECIO * DISKW USERS (STEM SORTIN. OPEN FINIS"
end
"FREE F(USERS)"
say "USERS Closed"

call wto "FTPD Install: Adding FTPAUTH facility class"


p1 = "FACILITYSVC244                                      FTPD    READ"
p2 = "FACILITYFTPAUTH                                             NONE"
p3 = "FACILITYFTPAUTH                                     ADMIN   READ"


"ALLOC FI(PROFILES) DA('SYS1.SECURE.CNTL(PROFILES)') SHR "
"EXECIO * DISKR PROFILES (FINIS STEM sortin."

if rc > 0 then do
    say "Error reading SYS1.SECURE.CNTL(PROFILES):" rc
    "FREE F(PROFILES)"
    exit 8
end
not_already_installed = 1
do i = 1 to sortin.0
    if pos(p1, sortin.i) > 0 then not_already_installed = 0
    if pos(p2, sortin.i) > 0 then not_already_installed = 0
    if pos(p3, sortin.i) > 0 then not_already_installed = 0
end

if not_already_installed then do
    x = sortin.0 + 1; sortin.x = p1
    x = sortin.0 + 2; sortin.x = p2
    x = sortin.0 + 3; sortin.x = p3
    sortin.0 = x

    CALL RXSORT
    "EXECIO * DISKW PROFILES (STEM SORTIN. OPEN FINIS"
end

"FREE F(PROFILES)"
call wto "FTPD Users and profiles installed"
/*
//SYSUT2   DD DSN=SYS2.EXEC(RAKFUPDT),DISP=SHR
//* **********************************************************
//EXECSORT EXEC PGM=IKJEFT01,REGION=8192K
//SYSTSIN  DD   *
FREE FILE(RXLIB)
ALLOC FILE(RXLIB) DSN('BREXX.CURRENT.RXLIB') SHR
FREE FILE(SYSEXEC)
ALLOC FILE(SYSEXEC) DSN('SYS2.EXEC') SHR
RX SYS2.EXEC(RAKFUPDT)
//SYSTSPRT DD   SYSOUT=*
//RAKFUSER EXEC RAKFUSER
//RAKFPROF EXEC RAKFPROF

'''

with open(sys.argv[1],"r") as infile:
    with open ("install.jcl","w") as outfile:
        outfile.write(install_jcl.format(ftpd_conf=infile.read().rstrip()))