TGT_DIRECTORY='/Users/admin/Code/fiosa/dist/fiosa' # Replace
echo "---------------------------------"
echo "Installing to $TGT_DIRECTORY. Please change variable within build_mac_app.sh to change this. Continuing."
echo "---------------------------------"

/usr/local/bin/platypus --app-icon '/Applications/Platypus.app/Contents/Resources/PlatypusDefault.icns'  --name 'Fiosa'  --interface-type 'None'  --interpreter '/bin/sh'  --interpreter-args '-exec' $TGT_DIRECTORY -y