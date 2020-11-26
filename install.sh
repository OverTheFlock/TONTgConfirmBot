#!/bin/bash

sudo apt update
sudo apt -y install python3-pip
pip3 install --upgrade pyTelegramBotAPI


# bot directory
BOTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd -P)"
BOTDIRDB="$BOTDIR/db"
IDDAT="$BOTDIRDB/id.dat"
[ ! -d "$BOTDIRDB" ] && mkdir -p "$BOTDIRDB"
if [ ! -f $IDDAT ]; then
    touch $IDDAT
fi
#tc=$(curl -s -L https://api.github.com/repos/tonlabs/tonos-cli/releases/latest | grep browser_download_url | cut -d '"' -f 4)
#wget -qO- $tc | tar -zxvf -
wget -qO- https://github.com/tonlabs/tonos-cli/releases/download/v0.1.13/tonos-cli_v0.1.13_linux.tar.gz | tar -zxvf -

# abi & tvc 
wget https://raw.githubusercontent.com/tonlabs/ton-labs-contracts/master/solidity/safemultisig/SafeMultisigWallet.abi.json
wget https://github.com/tonlabs/ton-labs-contracts/raw/master/solidity/safemultisig/SafeMultisigWallet.tvc
#remove old abi & tvc
rm SafeMultisigWallet.abi.json.*
rm SafeMultisigWallet.tvc.*

iUser="$(whoami)"
iGroup="$(id -gn)"

clear >$(tty)
# New installation 
if [ ! -f ./config.py ]; then
    # Tg id
    printf "\nRuning new installation\n\nPlease, provide your telegram id. You can get it by sending command /getid to bot @myidbot\n"
    read -p 'Telegram ID: ' itg
    itgcheck='^[0-9]{1}+$'
    while [[ ! $itg =~ $itgcheck ]]
    do
        printf "\nTelegram id supports only numbers.\n"
        read -p 'Telegram ID: ' itg
    done
    # Tg id

    # Tg bot api key
    printf "\n\n\nPlease, provide your telegram bot API key. You can create new bot with @BotFather\nFull instruction available here https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0\n"
    read -p 'Telegram bot API key: ' iTgBotAPIKey
    # Tg bot api key

    # Wallet
    printf "\n\n\nPlease, enter wallet, who will create transactions\n"
    read -p 'Wallet: ' iwallet
    # Wallet

    # Seed phrase
    printf "\n\n\nPlease, enter seed phrase, who will confirm transactions. It's different from wallet seed phrase\n"
    read -p 'Seed phrase: ' iseed
    # Seed phrase

    # Trusted contact
    printf "\n\n\nPlease, enter trusted contacts, for auto confirm transactions. Leave empty if not need.\n"
    printf "Example: '0:123...abc','-1:abc...000','0:abc...555'\n"
    printf "Without any spaces!\n"
    read -p 'Trusted contacts: ' itcontact
    # Trusted contact
fi

if [ -f ./config.py ]; then
    printf "\nRunning update\n\nPlease confirm values, or edit them if needed\n"
    

    # Tg id
    printf "\n\nPlease, confirm your telegram id. You can get it by sending command /id to bot @TONTgIDBot\n"
    itg="$(grep 'tg =' config.py | awk '{print $3}')"
    read -e -i "$itg" -p "Telegram ID: " input
    itg="${input:-$itg}"
    itgcheck='^[0-9]{1}+$'
    while [[ ! $itg =~ $itgcheck ]]
    do
        printf "\nTelegram id supports only numbers.\n"
        itg="$(grep 'tg =' config.py | awk '{print $3}')"
        read -e -i "$itg" -p "Telegram ID: " input
        itg="${input:-$itg}"
    done
    # Tg id

    # Tg bot api key
    printf "\n\n\nPlease, confirm your telegram bot API key. You can create new bot with @BotFather\nFull instruction available here https://docs.microsoft.com/en-us/azure/bot-service/bot-service-channel-connect-telegram?view=azure-bot-service-4.0\n"
    iTgBotAPIKey="$(grep 'TgBotAPIKey' config.py | awk '{print $3}' | tr -d \')"
    read -e -i "$iTgBotAPIKey" -p "Telegram bot API key: " input
    iTgBotAPIKey="${input:-$iTgBotAPIKey}"
    # Tg bot api key

    # Wallet
    printf "\n\n\nPlease, enter wallet, who will create transactions. Confirm wallet.\n"
    iwallet="$(grep 'wallet =' config.py | awk '{print $3}' | tr -d \')"
    read -e -i "$iwallet" -p "Wallet: " input
    iwallet="${input:-$iwallet}"
    # Wallet

    # Seed phrase
    printf "\n\n\nPlease, enter seed phrase, who will confirm transactions. It's different from wallet seed phrase. Confirm seed.\n"
    iseed="$(grep 'seed =' config.py | awk '{$1=$2="";print substr($0,3)}' | tr -d \')"
    read -e -i "$iseed" -p "Seed phrase:" input
    iseed="${input:-$iseed}"
    # Seed phrase

    # Trusted contact
    printf "\n\n\nPlease, enter trusted contacts, for auto confirm transactions. Leave empty if not need.\n"
    printf "Example: '0:123...abc','-1:abc...000','0:abc...555'\n"
    printf "Without any spaces!\n"
    itcontact="$(grep 'tcontact =' config.py | awk '{print $3}' | tr -d \[])"
    read -e -i "$itcontact" -p "Trusted contacts:" input
    itcontact="${input:-$itcontact}"
    # Trusted contact
fi




# config.py
bash -c 'cat > ./config.py' << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ##### TONTgConfirmBot Config
TgBotAPIKey = '$iTgBotAPIKey' # API Keythat you get from @BotFather
tg = $itg # Your id, you can get it by sending command /id to bot @TONTgIDBot
tontgcpath = '$BOTDIR' # User folder with this bot.
tontgcpathdb = '$BOTDIRDB' # User folder with bot database.
seed = '$iseed'
wallet = '$iwallet' # Wallet
tcontact = [$itcontact] # Trusted contacts for autoconfirm. Example ['0:123...abc','-1:abc...000','0:abc...555']
EOF
# config.py







echo "Copy files"

# /etc/init.d/tontgconfirmbot
sudo bash -c 'cat > /etc/init.d/tontgconfirmbot' << EOF
#!/bin/bash

### BEGIN INIT INFO
# Provides:          scriptname
# Required-Start:    \$remote_fs \$syslog
# Required-Stop:     \$remote_fs \$syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

NAME=tgconfirmbot
PIDFILE=$BOTDIR/tontgconfirmbot.pid
DAEMON=$BOTDIR/bot.py

case "\$1" in
  start)
        echo -n "Starting TON Confirmation telegram bot: "\$NAME
    start-stop-daemon --start --quiet --pidfile \$PIDFILE --exec \$DAEMON -- \$DAEMON_OPTS
        echo "."
    ;;
  stop)
        echo -n "Stopping TON Confirmation telegram bot: "\$NAME
    start-stop-daemon --stop --quiet --oknodo --pidfile \$PIDFILE
        echo "."
    ;;
  restart)
        echo -n "Restarting TON Confirmation telegram bot: "\$NAME
    start-stop-daemon --stop --quiet --oknodo --retry 15 --pidfile \$PIDFILE
    start-stop-daemon --start --quiet --pidfile \$PIDFILE --exec \$DAEMON -- \$DAEMON_OPTS
    echo "."
    ;;

  *)
    echo "Usage: "\$1" {start|stop|restart}"
    exit 1
esac

exit 0
EOF
sudo chmod -v +x /etc/init.d/tontgconfirmbot
# /etc/init.d/tontgconfirmbot

# /etc/systemd/system/tontgconfirmbot.service
sudo bash -c 'cat > /etc/systemd/system/tontgconfirmbot.service' << EOF
[Unit]
Description=TONTgConfirmBot
After=syslog.target

[Service]
Type=simple
User=$iUser
Group=$iGroup
ExecStart=/etc/init.d/tontgconfirmbot start
ExecStop=/etc/init.d/tontgconfirmbot stop

[Install]
WantedBy=multi-user.target
EOF
# /etc/systemd/system/tontgconfirmbot.service

chmod -v +x ./bot.py
sudo systemctl daemon-reload
echo "Starting service"
sudo systemctl stop tontgconfirmbot.service
sleep 3
sudo systemctl start tontgconfirmbot.service
sleep 2
sudo systemctl enable tontgconfirmbot.service
echo "Service tontgconfirmbot status"
systemctl status tontgconfirmbot.service
