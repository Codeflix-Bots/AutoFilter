#Dont change anything without informing us
if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Codeflix-Bots/AutoFilter.git /AutoFilter
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /AutoFilter
fi
cd /AutoFilter
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
