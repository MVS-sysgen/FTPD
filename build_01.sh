echo "Generating 01_assemble_ftp_objects.ebcdic.jcl"
cd $(dirname $0)
rdrprep build_01_assemble_ftp_objects.template build_01_assemble_ftp_objects.ebcdic.jcl
echo "Done"
