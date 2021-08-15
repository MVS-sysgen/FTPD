//INSTPROC JOB (FTPD),
//            'Make FTP Daemon',
//            CLASS=A,
//            MSGCLASS=A,
//            REGION=8M,
//            MSGLEVEL=(1,1),
//            USER=IBMUSER,PASSWORD=SYS1
//DELETE    EXEC  PGM=IDCAMS
//MYMEMBER  DD DISP=SHR,DSN=SYS2.PROCLIB(FTPD)
//SYSPRINT  DD    SYSOUT=A
//SYSIN     DD    *
    DELETE SYS2.PROCLIB(FTPD)
    SET MAXCC=0
/*
//FTPDDEVC EXEC PGM=IEBGENER
//SYSUT1   DD DATA,DLM=@@
//FTPD   PROC PASVADR='127,0,0,1',SRVIP='any',SRVPORT=21021
//********************************************************************
//*
//* MVS3.8j RAKF Enabled FTP server PROC
//* To use: in Hercules console issue /s FTPD to start FTP server on
//*         on port 2121
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