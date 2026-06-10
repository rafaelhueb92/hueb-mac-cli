echo "Preparing to install plugins . . . "
brew install figlet lolcat
TITLE="HUEB CLI"
figlet -f slant $TITLE | lolcat
chmod +x hueb.py
sudo ln -sf "$(pwd)/app.py" /usr/local/bin/hueb