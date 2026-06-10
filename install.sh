echo "Preparing to install plugins . . . "
brew install figlet lolcat
TITLE="HUEB CLI"
figlet -f slant $TITLE | lolcat
PYTHON_SCRIPT="https://raw.githubusercontent.com/rafaelhueb92/hueb-mac-cli/refs/heads/master/app.py"
curl -o hueb.py $PYTHON_SCRIPT 
chmod +x "$(pwd)/hueb.py"
mv "$(pwd)/hueb.py" ~/hueb.py
sudo ln -s ~/hueb.py /usr/local/bin/hueb
hueb -h