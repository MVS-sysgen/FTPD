//PKGEFTPD JOB (FTPD),
//            'FTPD XMI',
//            CLASS=A,
//            MSGCLASS=A,
//            REGION=8M,
//            MSGLEVEL=(1,1),
//            USER=IBMUSER,PASSWORD=SYS1
//*
//* ------------------------------------------------------------------
//* DELETE DATASETS IF ALREADY CREATED
//* ------------------------------------------------------------------
//*
//FTDELETE EXEC PGM=IDCAMS,REGION=1024K
//SYSPRINT DD  SYSOUT=A
//SYSIN    DD  *
 DELETE SYSGEN.FTPD.LINKLIB NONVSAM SCRATCH PURGE
 DELETE SYSGEN.FTPD.XMIT NONVSAM SCRATCH PURGE
 /* IF THERE WAS NO DATASET TO DELETE, RESET CC           */
 IF LASTCC = 8 THEN
   DO
       SET LASTCC = 0
       SET MAXCC = 0
   END
/*
//*
//* ------------------------------------------------------------------
//* COPY FTPD and FTPD to SYSGEN.FTPD.LINKLIB
//* ------------------------------------------------------------------
//*
//COPYLL   EXEC PGM=IEBCOPY
//SYSPRINT DD SYSOUT=A
//SYSUT1 DD DSN=SYS2.LINKLIB,DISP=SHR
//SYSUT2 DD DSN=SYSGEN.FTPD.LINKLIB,DISP=(,CATLG,DELETE),
//             UNIT=SYSDA,VOL=SER=PUB001,SPACE=(TRK,(20,,2)),
//             DCB=(RECFM=U,LRECL=0,BLKSIZE=19069)
//SYSIN DD *
   COPY OUTDD=SYSUT2,INDD=SYSUT1
   SELECT MEMBER=FTPD
   SELECT MEMBER=FTPDXCTL
/*
//*
//* ------------------------------------------------------------------
//* GENERATE XMIT SYSGEN.FTPD.XMIT using SYSGEN.FTPD.LINKLIB
//* ------------------------------------------------------------------
//*
//XMITLLIB EXEC PGM=XMIT370
//STEPLIB  DD DSN=SYSC.LINKLIB,DISP=SHR
//XMITLOG  DD SYSOUT=*
//SYSPRINT DD SYSOUT=*
//SYSIN    DD DUMMY
//SYSUT1   DD DSN=SYSGEN.FTPD.LINKLIB,DISP=SHR
//SYSUT2   DD DSN=&&SYSUT2,UNIT=SYSDA,
//         SPACE=(TRK,(255,255)),
//         DISP=(NEW,DELETE,DELETE)
//XMITOUT  DD DSN=SYSGEN.FTPD.XMIT,DISP=(,CATLG,DELETE),
//            UNIT=SYSDA,VOL=SER=PUB001,SPACE=(TRK,(50,50))