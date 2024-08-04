#Dont change anything without informing us
if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Codeflix-Bots/Lucy.git /Lucy
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /Lucy
fi
cd /Lucy
pip3 install -U -r requirements.txt
echo "sᴛᴀʀᴛɪɴɢ ʟᴜᴄʏ ʙᴏᴛ...."
python3 bot.py
