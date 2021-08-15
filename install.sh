# FTPD install script

echo "Generating Random FTPD user password"
cd $(dirname $0)

password=$(cat /dev/urandom 2>/dev/null| tr -dc 'A-Z0-9$@#' 2>/dev/null | head -c 8 )
#echo "FTPD User password: $password"
sed "s/12345678/$password/" 01_update_rakf.template > 01_update_rakf.jcl
sed -e '/###FTPD.CONF###/ {' -e 'r FTPD.conf' -e 'd' -e '}' 02_install_ftpd.template > 02_install_ftpd.jcl

echo "Done"
