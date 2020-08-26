#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
import config
import time
import datetime
import subprocess
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
telebot.logger.setLevel(logging.ERROR) # Outputs Error messages to console.
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

def cnfrmbtn(tid):
  try:
    bot.send_chat_action(config.tg, "typing")
    confrmcmd = "cd " + config.tontgcpath + " && ./tonos-cli call " + config.wallet + " confirmTransaction '{\"transactionId\":\"" + tid + "\"}' --abi SafeMultisigWallet.abi.json --sign \"" + config.seed + "\""
    confrmcmd = str(subprocess.check_output(confrmcmd, shell = True, encoding='utf-8',timeout=60))
    if "Succeeded" in confrmcmd:
      pass
    else:
      bot.send_message(config.tg, text="Confirmation error",parse_mode="Markdown")
  except:
    bot.send_message(config.tg, text="Confirmation error",parse_mode="Markdown")

def autocnfrm(tdest,tid):
  try:
    confrmcmd = "cd " + config.tontgcpath + " && ./tonos-cli call " + config.wallet + " confirmTransaction '{\"transactionId\":\"" + tid + "\"}' --abi SafeMultisigWallet.abi.json --sign \"" + config.seed + "\""
    confrmcmd = str(subprocess.check_output(confrmcmd, shell = True, encoding='utf-8',timeout=60))
    if "Succeeded" in confrmcmd:
      bot.send_message(config.tg, text="Auto Succeeded to " + tdest + "\nTransaction id:" + tid,parse_mode="Markdown")
    else:
      bot.send_message(config.tg, text="Auto confirmation error to " + tdest + "\nTransaction id:" + tid,parse_mode="Markdown")
  except:
    bot.send_message(config.tg, text="Auto confirmation error too " + tdest + "\nTransaction id:" + tid,parse_mode="Markdown")


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
                if tdest in config.tcontact:
                  autocnfrm(tdest,tid)
                  w.write(tid + "\n")
                  w.close()
                else:
                  ConfirmRejectKeyboard = types.InlineKeyboardMarkup()
                  RejectBtn = types.InlineKeyboardButton(text= "\U0000274C Reject ", callback_data="rejecttr")
                  ConfirmBtn = types.InlineKeyboardButton(text= "\U00002705 Confirm ", callback_data="confirmtr")
                  ConfirmRejectKeyboard.add(RejectBtn,ConfirmBtn)
                  bot.send_message(config.tg, text="*Creator:* " + tcreator + "\n*Destination:* " + tdest + "\n*ID:* " + tid + "\n*Value:* " + str(tvalue) + " \U0001F48E",parse_mode="Markdown",reply_markup=ConfirmRejectKeyboard)
                  w.write(tid + "\n")
                  w.close()
      except:
        time.sleep(10)
        tmr += 10
    else:
      time.sleep(10)
      tmr += 10

##
RejectedKeyboard = types.InlineKeyboardMarkup()
RejectedBtn = types.InlineKeyboardButton(text= "\U0000274C Rejected \U0000274C", callback_data="rejectedtr")
RejectedKeyboard.add(RejectedBtn)

WaitKeyboard = types.InlineKeyboardMarkup()
WaitBtn = types.InlineKeyboardButton(text= "\U000023F3 Confirmation in progress \U000023F3", callback_data="waittr")
WaitKeyboard.add(WaitBtn)

ConfirmedKeyboard = types.InlineKeyboardMarkup()
ConfirmedBtn = types.InlineKeyboardButton(text= "\U00002705 Confirmed \U00002705", callback_data="confirmedtr")
ConfirmedKeyboard.add(ConfirmedBtn)

### call data
@bot.callback_query_handler(func = lambda call: True)
def inlinekeyboards(call):
  if call.from_user.id == config.tg:
    if call.data == "rejecttr":
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=RejectedKeyboard)
    if call.data == "confirmtr":
      tid = str(call.message.text.split()[5])
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=WaitKeyboard)
      cnfrmbtn(tid)
      bot.edit_message_reply_markup(config.tg, message_id=call.message.message_id, reply_markup=ConfirmedKeyboard)
##

NewTransMonitoring = threading.Thread(target = NewTransMonitoring)
NewTransMonitoring.start()

while True:
  try:
    bot.polling(none_stop=True, timeout=10) #constantly get messages from Telegram
  except:
    bot.stop_polling()
    time.sleep(5)
