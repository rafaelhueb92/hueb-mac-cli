echo "Preparing to install plugins . . . "
brew install figlet lolcat
TITLE="HUEB CLI"
figlet -f slant $TITLE | lolcat
PYTHON_SCRIPT="https://raw.githubusercontent.com/rafaelhueb92/hueb-mac-cli/refs/heads/master/app.py"
curl -o app.py $PYTHON_SCRIPT 
chmod +x hueb.py
sudo mkdir -p /usr/local/bin/hueb && mv "$(pwd)/hueb.py" /usr/local/bin/hueb
hueb -h