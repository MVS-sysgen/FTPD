# generates the JCL needed to build the HLASM files

from pathlib import Path
import sys

if len(sys.argv) == 1:
    print("usage: {} /path/to/FTPD/hlasm".format(sys.argv[0]))
    sys.exit(-1)


JCL_header = '''//MAKEFTPD JOB (FTPD),
//            'Make FTP Daemon',
//            CLASS=A,
//            MSGCLASS=A,
//            REGION=8M,
//            MSGLEVEL=(1,1),
//            USER=IBMUSER,PASSWORD=SYS1
//*********************************************************************
//*
//* Name: MAKEXCTL
//*
//* Desc: Assemble and link FTPD Wrapper
//*
//*********************************************************************
//*
//* Create temp PDS for output to punchcard writer
//*
//MAKEOBJ EXEC PGM=IEFBR14
//OUTPUT  DD DSN=&&OBJ,DISP=(,PASS),SPACE=(TRK,3),UNIT=VIO,
//        DCB=(RECFM=FB,LRECL=80,BLKSIZE=3200)
//*
//* Assemble/link FTPDXCTL to SYS2.LINKLIB
//*
//ASMCL   EXEC ASMFCL,PARM.ASM=(OBJ,NODECK,NOXREF),
//        MAC1='SYS1.AMODGEN',MAC2='SYS2.MACLIB'
//ASM.SYSIN DD *
{FTPDXCTL}
//LKED.SYSLMOD DD DSN=SYS2.LINKLIB(FTPDXCTL),DISP=SHR
//* 
//* ********************************
//* Make sure the punchcard writer on device D (Class B)
//* is reset 
//* 
//* ********************************
//*
'''

assemble_objects = '''//* Assemble {filename}
//*
//{filename:<8} EXEC ASMFC,PARM.ASM=(OBJ,NODECK),MAC1='SYS2.MACLIB',
//         MAC2='SYS1.AMODGEN'
//ASM.SYSIN DD *
{file_contents}
/*
//ASM.SYSGO DD DSN=&&OBJ,DISP=(MOD,PASS)
//*
'''

jcl_footer = '''//* Now to output the temp dataset &&OBJ to Class B which is the
//* punch out (pch00d.txt or changed to ftpdrakf.punch using)
//PUNCHOUT EXEC PGM=IEBGENER
//SYSIN    DD DUMMY
//SYSUT1   DD DSN=&&OBJ,DISP=SHR
//SYSUT2   DD SYSOUT=B
//SYSPRINT DD SYSOUT=*
'''

p = Path(sys.argv[1]).glob('**/*.hlasm')
print("*** Parsing files in {}".format(sys.argv[1]))
files = [x for x in p if x.is_file()]
asm = ''
for asm_file in sorted(files):
    print("*** File: {}".format(asm_file))
    if "FTPDXCTL" in str(asm_file):
        with open (asm_file,"r") as FTPDXCTL:
            header = JCL_header.format(FTPDXCTL=FTPDXCTL.read().rstrip())
    else:

        with open (asm_file,"r") as objectasm:
            asm += assemble_objects.format(filename=asm_file.stem, file_contents=objectasm.read().rstrip())

print("*** Writting: assemble_ftprakf.jcl")
with open ("assemble_ftprakf.jcl","w") as outfile:
    outfile.write(header+asm+jcl_footer.rstrip())