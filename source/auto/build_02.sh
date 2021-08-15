set -e
cd $(dirname $0)
pwd
echo "Stripping punch card info:"
dd if=ftpdrakf.punch bs=1 skip=160 count=2720 of=ftpdrac.pch
echo "Replacing function names"
./jcc/objscan ftpdrac.pch objscan_input.nam ftpdrac.obj
echo "Compiling ftpd.c"
./jcc/jcc -I./jcc/include -I./ -D__MVS_ -o -list=list.out ftpd.c
echo "linking object files to ftpd.load"
./jcc/prelink -r jcc/objs ftpd.load ftpd.obj ftpdrac.obj
echo "creating JCL to install FTPDDEV to SYS2.LINKLIB"
rdrprep build_03_link_ftpd.template build_03_link_ftpd.ebcdic.jcl
echo "Build 03 Completed"
