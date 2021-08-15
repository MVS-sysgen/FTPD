//MAKEFTPD JOB (FTPD),
//            'Make FTP Daemon',
//            CLASS=A,NOTIFY=JUERGEN,
//            MSGCLASS=J,
//            REGION=8M,
//            MSGLEVEL=(1,1)
/*JOBPARM ROOM=JW
//********************************************************************
//*
//* Name: MAKEFTPD
//*
//* Desc: Assemble RAC support routines, compile and link FTPD
//*
//********************************************************************
//*
//* assemble RAC support
//*
//FTPLOGIN EXEC ASMFC,PARM.ASM=(OBJ,NODECK),MAC1='SYS2.MACLIB',
//         MAC2='SYS1.AMODGEN'
//ASM.SYSIN DD DSN=JUERGEN.FTPD.RAC.ASM(FTPLOGIN),DISP=SHR
//ASM.SYSGO DD DSN=&&OBJ,DISP=(,PASS),SPACE=(TRK,3),UNIT=VIO,
//        DCB=(RECFM=FB,LRECL=80,BLKSIZE=3200)
//FTPLGOUT EXEC ASMFC,PARM.ASM=(OBJ,NODECK),MAC1='SYS2.MACLIB',
//         MAC2='SYS1.AMODGEN'
//ASM.SYSIN DD DSN=JUERGEN.FTPD.RAC.ASM(FTPLGOUT),DISP=SHR
//ASM.SYSGO DD DSN=&&OBJ,DISP=(MOD,PASS)
//FTPAUTH  EXEC ASMFC,PARM.ASM=(OBJ,NODECK),MAC1='SYS2.MACLIB',
//         MAC2='SYS1.AMODGEN'
//ASM.SYSIN DD DSN=JUERGEN.FTPD.RAC.ASM(FTPAUTH),DISP=SHR
//ASM.SYSGO DD DSN=&&OBJ,DISP=(MOD,PASS)
//FTPSU    EXEC ASMFC,PARM.ASM=(OBJ,NODECK),MAC1='SYS2.MACLIB',
//         MAC2='SYS1.AMODGEN'
//ASM.SYSIN DD DSN=JUERGEN.FTPD.RAC.ASM(FTPSU),DISP=SHR
//ASM.SYSGO DD DSN=&&OBJ,DISP=(MOD,PASS)
//O         DD DISP=(,PASS),DSN=&&ALLOBJ,UNIT=SYSDA,
//          DCB=(RECFM=FB,LRECL=80,BLKSIZE=3200),SPACE=(TRK,(30,10,30))
//*
//* ESD to XSD conversion for long names
//*
//SCAN    EXEC PGM=OBJSCAN,
//        PARM='//DDN:I //DDN:N //DDN:O'
//STEPLIB   DD DSN=JCC.LINKLIB,DISP=SHR
//STDOUT    DD SYSOUT=*
//I         DD DSN=&&OBJ,DISP=(OLD,DELETE)
//O         DD DISP=(OLD,PASS),DSN=&&ALLOBJ(FTPDRAC)
//N         DD *
FTPLOGIN rac_user_login
FTPLGOUT rac_user_logout
FTPAUTH rac_ftp_auth
FTPSU rac_switch_user
/*
//*
//* merge RAC support routines with JCC library
//*
//COPYCLIB EXEC PGM=IEBCOPY
//SYSUT1   DD  DISP=SHR,DSN=JCC.OBJ
//SYSUT2   DD  DISP=(OLD,PASS),DSN=&&ALLOBJ
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//*
//*
//*
//COPYINDX EXEC PGM=IEBGENER
//SYSUT1   DD  DISP=SHR,DSN=JCC.OBJ(LIBLST)
//         DD  *
ftpdrac
/*
//SYSUT2   DD  DISP=(OLD,PASS),DSN=&&ALLOBJ(LIBLST)
//SYSPRINT DD  DUMMY
//SYSIN    DD  DUMMY
//*
//* compile and link FTPD
//*
//JCCCL   EXEC JCCCL,INFILE='JUERGEN.FTPD.RAC.SRC(FTPD)',
//        OUTFILE='JUERGEN.FTPD.RAC.LOAD(FTPD)'
//COMPILE.JCCINCS DD DISP=SHR,DSN=JUERGEN.FTPD.RAC.INCLUDE
//PRELINK.L DD DSN=&&ALLOBJ,DISP=(OLD,DELETE)
//