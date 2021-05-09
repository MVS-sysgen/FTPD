echo "Generating 01_assemble_ftp_objects.ebcdic.jcl"
cd $(dirname $0)
rdrprep 01_assemble_ftp_objects.template 01_assemble_ftp_objects.ebcdic.jcl
echo "Done"
