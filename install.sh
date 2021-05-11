# FTPD install script

echo "Generating Random FTPD password"
cd $(dirname $0)

password=$(cat /dev/urandom 2>/dev/null| tr -dc 'A-Z0-9$@#' 2>/dev/null | head -c 8 )
echo "Using: $password"
sed "s/12345678/$password/" 01_update_rakf.template > 01_update_rakf.jcl

echo "Done"
