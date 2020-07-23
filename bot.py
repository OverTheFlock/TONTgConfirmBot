#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import config
import time
import datetime
import subprocess
import tty
import pty
import psutil
import json
import logging
import threading
import re
import telebot
from telebot import types
from telebot import util


# ##### TONTgBot

# API Token
bot = telebot.TeleBot(config.TgBotAPIKey)
# /API Token

# ##### TONTgBot


# Log
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG) # Outputs Error messages to console.
# /Log

# Start
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  if message.from_user.id == config.tg:
    bot.send_message(config.tg, "Hello" + "\U0001F44B\n" + "I'm here to help you with your TON transactions confirmation " + " \U0001F9BE\n" + "I will notify you")
  else:
    pass
# /Start

# Confirmation
@bot.message_handler(commands=["confirm"])
def cnfrm(message):
  if message.from_user.id == config.tg:
    try:
      bot.send_chat_action(config.tg, "typing")
      trid = message.text.split()
      trid = str(trid[1])
      confrmcmd = "cd " + config.tontgcpath + " && ./tonos-cli call " + config.wallet + " confirmTransaction '{\"transactionId\":\"" + trid + "\"}' --abi SafeMultisigWallet.abi.json --sign \"" + config.seed + "\""
      confrmcmd = str(subprocess.check_output(confrmcmd, shell = True, encoding='utf-8',timeout=60))
      if "Succeeded" in confrmcmd:
        bot.send_message(config.tg, text="Succeeded",parse_mode="Markdown")
      else:
        bot.send_message(config.tg, text="Confirmation error",parse_mode="Markdown")
    except:
      bot.send_message(config.tg, text="Confirmation error",parse_mode="Markdown")






def NewTransMonitoring():
  tmr = 0
  while True:
    if tmr == 10:
      try:
        tmr = 0
        confrmcheck = "cd " + config.tontgcpath + " && ./tonos-cli run " + config.wallet + " getTransactions {} --abi SafeMultisigWallet.abi.json | sed  -n '/Result:/ ,$ p' | sed 's/Result://g'"
        confrmcheck = str(subprocess.check_output(confrmcheck, shell = True, encoding='utf-8',timeout=60))
        resultcheck = json.loads(confrmcheck)
        for i in resultcheck['transactions']:
          tcreator = i['creator'][2:]
          tdest = i['dest']
          tid = i['id']
          tvalue = i['value']
          tvalue = int(str(tvalue[2:]), 16)
          tvalue = tvalue/10**9
          with open(os.path.join(config.tontgcpathdb, "id.dat"), "r") as i:
            if tid in i.read():
              pass
            else:
              with open(os.path.join(config.tontgcpathdb, "id.dat"), "a") as w:
                bot.send_message(config.tg, text="*Creator:*" + tcreator + "\n*Destination:*" + tdest + "\n*ID:*" + tid + "\n*Value:*" + str(tvalue) + " \U0001F48E",parse_mode="Markdown")
                w.write(tid + "\n")
                w.close()
      except:
        time.sleep(10)
        tmr += 10
    else:
      time.sleep(10)
      tmr += 10




NewTransMonitoring = threading.Thread(target = NewTransMonitoring)
NewTransMonitoring.start()

while True:
  try:
    bot.polling(none_stop=True, timeout=10) #constantly get messages from Telegram
  except:
    bot.stop_polling()
    time.sleep(5)
