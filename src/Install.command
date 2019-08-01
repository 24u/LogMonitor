_path_to_me="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)/LogMonitor"

_folder_name="$( basename "${_path_to_me}" )"

echo "******************************************************"
echo "The installer is using sudo to install LogMonitor. Therefore Your sudo user password is needed. Please type it below:"
sudo mkdir -p  "/Library/Application Support/24U"
sudo cp -rf "$_path_to_me" "/Library/Application Support/24U"

_path_to_me="/Library/Application Support/24U/$_folder_name"

_path_to_plist="$_path_to_me/com.24usoftware.LogMonitor.plist"
_path_to_server="$_path_to_me/LogMonitor.py"
sudo chmod +x "$_path_to_server"

sudo /usr/libexec/PlistBuddy -c "Set :Program $_path_to_server" "$_path_to_plist"

sudo chown root:wheel "$_path_to_plist"
sudo cp -f "$_path_to_plist" "/Library/LaunchDaemons"

sudo chmod o-w /Library/LaunchDaemons/*

_path_to_plist="/Library/LaunchDaemons/com.24usoftware.LogMonitor.plist"

launchctl unload "$_path_to_plist" 2>/dev/null

open "$_path_to_me"

sudo chmod -R 777 "/Library/Application Support/24U"/*
#sudo chflags nouchg "$_path_to_me/LogMonitorConfig.txt"
open "$_path_to_me/LogMonitorConfig.txt"

echo "- ! -"
echo "For LogMonitor to work properly it is necessary to update the LogMonitorConfig.txt configuration file."
read -p "Press any key when you are done." -n1 -s
echo "- ! -"

sudo launchctl load -w "$_path_to_plist"

if [[ $(sudo launchctl list | grep com.24usoftware.LogMonitor) != "" ]]
then
  echo "LogMonitor successfully started!"
else
  echo "LogMonitor could not be started!"
fi
