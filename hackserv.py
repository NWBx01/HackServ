#!/usr/bin/env python3
#
# HackServ IRC Bot
# hackserv.py
#
# Copyright (c) 2018-2024 Stephen Harris <trackmastersteve@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

legal_notice = 'THIS BOT IS FOR EDUCATION PURPOSES ONLY! DO NOT USE IT FOR MALICIOUS INTENT!'
author = 'Stephen Harris (trackmastersteve@gmail.com)'
github = 'https://github.com/trackmastersteve/hackserv.git'
software = 'HackServ'
version = '1.3.5'
last_modification = '2023.12.15'

# Imports
import os
import ssl
import sys
import stat
import nmap
import time
import uuid
import shlex
import shutil
import base64
import random
import socket
import logging
import datetime
import platform
import threading
import subprocess
import urllib.request
from requests import get

from pynput.keyboard import Key, Listener
logging.basicConfig(filename=("keylog.txt"), level=logging.DEBUG, format=" %(asctime)s - %(message)s") # Text file to save keylogger data.
#starttime = datetime.datetime.utcnow() # Start time is used to calculate uptime.
ip = get('https://api.ipify.org').text # Get public IP address. (used to set botnick-to-ip as well as the '.ip' command.)
sys.path.insert(0, '/usr/local/bin/') # Working directory.
from hsConfig import * # import the hsConfig.py file.
lastpingreceived = time.time() # Time at last received PING.
lastpingsent = time.time() # Time at last sent PING.
threshold = 200 # Ping timeout before reconnect.
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Set ircsock variable.
if usessl: # If SSL is True, connect using SSL.
    ssl_context = ssl.create_default_context()
    if selfSignedCerts:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    ircsock = ssl_context.wrap_socket(ircsock, server_hostname=server)
ircsock.settimeout(60) # Set socket timeout.
connected = False # Variable to say if bot is connected or not.

from llm_commands import *

if sd_status == True:
    stablediffusion = StableDiffusion()
    
if llm_api_status == True:
    gpt3 = LLM_API()
    gpt3.prompt("hi", 512, 5)
    
if (llm_proxy_status == True):
    chatgpt = LLM_Proxy()
    
if (otakuchan_status == True):
    otakuchan = LLM_Proxy()


################## IRC Stuff Here #####################
#######################################################

message_queue = []

def ircsend(msg):
    ircsock.send(bytes(str(msg) +"\n", "UTF-8")) # Send data to IRC server.

def connect(): # Connect to the IRC network.
    global connected
    while not connected:
        try: # Try and connect to the IRC server.
            if debugmode: # If debugmode is True, msgs will print to screen.
                print("Connecting to " + str(server) + ":" + str(port))
            ircsock.connect_ex((server, port)) # Here we connect to the server.
            if usesasl:
                ircsend("CAP REQ :sasl") # Request SASL Authentication.
                if debugmode:
                    print("Requesting SASL login.")
            if useservpass: # If useservpass is True, send serverpass to server to connect.
                ircsend("PASS "+ serverpass) # Send the server password to connect to password protected IRC server.
            ircsend("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick+ " "+ botnick) # We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
            ircsend("NICK "+ botnick) # Assign the nick to the bot.
            connected = True
            #main()
            threading.Thread(target=irc_receive).start()
            threading.Thread(target=ping_server).start()
            threading.Thread(target=main).start()
        except Exception as iconnex: # If you can't connect, wait 10 seconds and try again.
            if debugmode: # If debugmode is True, msgs will print to screen.
                print("Exception: " + str(iconnex))
                print("Failed to connect to " + str(server) + ":" + str(port) + ". Retrying in 2 seconds...")
            connected = False
            time.sleep(2)
            reconnect()

def reconnect(): # Reconnect to the IRC network.
    global connected # Set 'connected' variable
    global ircsock # Set 'ircsock' variable
    while not connected:
        ircsock.close() # Close previous socket.
        ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Set ircsock variable.
        if usessl: # If SSL is True, connect using SSL.
            ssl_context = ssl.create_default_context()
            if selfSignedCerts:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            ircsock = ssl_context.wrap_socket(ircsock, server_hostname=server)
        try:
            if debugmode: # If debugmode is True, msgs will print to screen.
                print("Reconnecting to " + str(server) + ":" + str(port))
            ircsock.connect_ex((server, port)) # Here we connect to the server.
            if usesasl:
                ircsend("CAP REQ :sasl") # Request SASL Authentication.
                if debugmode:
                    print("Requesting SASL login.")            
            if useservpass: # If useservpass is True, send serverpass to server to connect.
                ircsend("PASS "+ serverpass) # Send the server password to connect to password protected IRC server.
            ircsend("USER "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick +" "+ botnick) # We are basically filling out a form with this line and saying to set all the fields to the bot nickname.
            ircsend("NICK "+ botnick) # Assign the nick to the bot.
            connected = True
            #main()
            threading.Thread(target=irc_receive).start()
            threading.Thread(target=ping_server).start()
            threading.Thread(target=main).start()
        except Exception as irconnex: # If you can't connect, wait 10 seconds and try again.
            if debugmode: # If debugmode is True, msgs will print to screen.
                print("Exception: " + str(irconnex))
                print("Failed to reconnect to " + str(server) + ":" + str(port) + ". Retrying in 2 seconds...")
            connected = False
            time.sleep(2)
            reconnect()
            
def joinchan(chan): # Join channel(s).
    ircsend("JOIN "+ chan)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "JOIN "+ chan) # Print messages to the screen. (won't allow bot to run in the background.)
       
    #ircmsg = ""
    #while ircmsg.find("End of /NAMES list.") == -1:
    #    ircmsg = ircsock.recv(2048).decode("UTF-8")
    #    ircmsg = ircmsg.strip('\n\r')
    #    if debugmode: # If debugmode is True, msgs will print to screen.
    #        print(ircmsg) # Print messages to the screen. (won't allow bot to run in the background.)

def partchan(chan): # Part channel(s).
    ircsend("PART "+ chan)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "PART "+ chan) # Print messages to the screen. (won't allow bot to run in the background.)
        
def pjchan(chan): # Part then Join channel(s) 
    ircsend("PART "+ chan)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "PART "+ chan) # Print messages to the screen. (won't allow bot to run in the background.)
    ircsend("JOIN "+ chan)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "JOIN "+ chan) # Print messages to the screen. (won't allow bot to run in the background.)
    
def newnick(newnick): # Change botnick.
    ircsend("NICK "+ newnick)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "NICK "+ newnick) # Print messages to the screen. (won't allow bot to run in the background.)

def sendmsg(msg, target=channel): # Sends messages to the target.
    ircsend("PRIVMSG "+ target +" :"+ msg)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "PRIVMSG "+ target +" :"+ msg) # Print messages to the screen. (won't allow bot to run in the background.)

def sendact(msg, target=channel): # Sends an ACTION to the target.
    ircsend("PRIVMSG " + target + " :ACTION " + msg + "")
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "PRIVMSG " + target + " :ACTION " + msg + "") # Print messages to the screen. (won't allow bot to run in the background.)

def sendtopic(msg, target=channel): # Sends topic to the target.
    ircsend("TOPIC "+ target +" :"+ msg)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "TOPIC "+ target +" :"+ msg) # Print messages to the screen. (won't allow bot to run in the background.)

def sendntc(ntc, target=channel): # Sends a NOTICE to the target.
    ircsend("NOTICE "+ target +" :"+ ntc)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "NOTICE "+ target +" :"+ ntc) # Print messages to the screen. (won't allow bot to run in the background.)

def sendping(): # Sends a NOTICE to the target.
    pingtime = int(time.time())
    ircsend("PING LAG" + str(pingtime))
    #if debugmode: # If debugmode is True, msgs will print to screen.
    #    print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "PING LAG" + str(pingtime)) # Print messages to the screen. (won't allow bot to run in the background.)
    
def sendversion(nick, ver): # Respond to VERSION request.
    ver = "VERSION " + software + ' ' + version + ' Download it at: ' + github
    sendntc(ver, nick)
    if debugmode: # If debugmode is True, msgs will print to screen.
        print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + "NOTICE "+ nick +" :"+ ver) # Print messages to the screen. (won't allow bot to run in the background.)

# These following functions are of dubious necessity.
'''
def kick(msg, usr, chan): # Kick a user from the channel.
    ircsend("KICK "+ chan + " " + usr + " :"+ msg)
    
def uptime(): # Used to get current uptime for .uptime command
    delta = datetime.timedelta(seconds=round((datetime.datetime.utcnow() - starttime).total_seconds()))
    return delta
'''   

# Pings the server if the time since the last ping is >= 15 seconds.
def ping_server():
    global connected
    global lastpingsent
    try:
        while connected:
            if (time.time() - lastpingsent) >= 15:
                sendping()
                lastpingsent = time.time()
    except:
        connected = False
        reconnect()

# Receives IRC messages and puts them into a message queue.
def irc_receive():
    global connected
    while connected:
        ircmsg = ircsock.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')

        if ircmsg:
            message_queue.append(ircmsg)

            if debugmode: # If debugmode is True, msgs will print to screen.
                if ircmsg.find("PONG") == -1:
                    print("[" + time.strftime("%H:%M:%S", time.localtime()) + "]: " + ircmsg) # Print messages to the screen. (won't allow bot to run in the background.)

        if not ircmsg: # If no response from server, try and reconnect.
            if debugmode: # If debugmode is True, msgs will print to screen.
                print('Disconnected from server')
            connected = False
            reconnect()

# This is the main function for all of the bot controls.
def main():
    global connected
    global botnick
    global ip
    global lastpingreceived
    global lastpingsent
    while connected:
        if message_queue: 
            ircmsg = message_queue.pop(0)
        
            # SASL Authentication.
            if ircmsg.find("ACK :sasl") != -1:
                if usesasl:
                    if debugmode: # If debugmode is True, msgs will print to screen.
                        print("Authenticating with SASL PLAIN.") # Request PLAIN Auth.
                    ircsend("AUTHENTICATE PLAIN")
            if ircmsg.find("AUTHENTICATE +") != -1:
                if usesasl:
                    if debugmode: # If debugmode is True, msgs will print to screen.
                        print("Sending %s Password: %s to SASL." % (nickserv, nspass))
                    authpass = botnick + '\x00' + botnick + '\x00' + nspass
                    ap_encoded = str(base64.b64encode(authpass.encode("UTF-8")), "UTF-8")
                    ircsend("AUTHENTICATE " + ap_encoded) # Authenticate with SASL.
            if ircmsg.find("SASL authentication successful") != -1:
                if usesasl:
                    if debugmode: # If debugmode is True, msgs will print to screen.
                        print("Sending CAP END command.")
                    ircsend("CAP END") # End the SASL Authentication.
            
            # Wait 30 seconds and try to reconnect if 'too many connections from this IP'
            if ircmsg.find('Too many connections from your IP') != -1:
                if debugmode: # If debugmode is True, msgs will print to screen.
                    print("Too many connections from this IP! Reconnecting in 30 seconds...")
                connected = False
                time.sleep(30)
                reconnect()
            
            # Change nickname if current nickname is already in use.
            if ircmsg.find('Nickname is already in use') != -1:
                #botnick = "hs[" + str(random.randint(10000,99999)) +"]"
                botnick = botnick + "[" + str(random.randint(10000,99999)) +"]"
                newnick(botnick)
            
            # Join 'channel' and msg 'admin' after you are fully connected to server.
            if ircmsg.find('NOTICE') != -1:
                name = ircmsg.split('!',1)[0][1:]
                message = ircmsg.split('NOTICE',1)[1].split(':',1)[1]
                if message.find('*** You are connected') != -1:
                    #sendmsg("IDENTIFY %s" % nspass, nickserv)
                    #joinchan(channel)
                    #sendntc(format(ip) + " Online!", adminname)
                    pass
                    
                # Respond to 'PONG ERROR' message from server.
                if message.find('ERROR') != -1:
                    if debugmode: # If debugmode is True, msgs will print to screen.
                        print("Received a 'ERROR' from the server, reconnecting in 5 seconds...")
                    connected = False
                    time.sleep(5)
                    reconnect()
                
                # Respond to NickServ ident request.
                if name.lower() == nickserv.lower() and message.find('This nickname is registered') != -1:
                    sendmsg("IDENTIFY " + nspass, nickserv)

            # Join 'channel' upon reading Rizon/Sageru startup msg and login
            if (ircmsg.find('CALLERID') != -1) or (ircmsg.find('End of /MOTD command') != -1):
                if (server == "irc.rizon.net"):
                    sendmsg("IDENTIFY " + nspass, nickserv)
                    sendmsg("ON", "HostServ")
                    time.sleep(5)
                    sendmsg(botnick + " is now online.", adminname)
                joinchan(channel)
                joinchan(channel2)

            # Respond to CTCP VERSION.
            if ircmsg.find('VERSION') != -1:
                name = ircmsg.split('!',1)[0][1:]
                vers = version
                sendversion(name, vers)
                
            # Things to do when a user joins the channel.
            if ircmsg.find('JOIN') != -1:
                name = ircmsg.split('!',1)[0][1:] # Username
                message = ircmsg.split('JOIN',1)[1].split(':',1)[1] # Channel
                ipHost = ircmsg.split('JOIN',1)[0] #IP Address or Hostname
                if len(name) < 17:
                    if message.find(channel) != -1:
                        if onJoin: # must have 0nJoin = True in hsConfig.
                            #ircsend("DNS "+ name) # Attempt to get users IP address using DNS from IRC Server. (Commented out due to Oper requirements on most servers.)
                            #sendntc('User: '+ name +' Hostname: '+ ipHost +' Joined: '+ message, adminname)
                            pass
                
            # Messages come in from IRC in the format of: ":[Nick]!~[hostname]@[IPAddress]PRIVMSG[channel]:[message]"
            # This is the main text delimiting + response portion of the program
            if ircmsg.find('PRIVMSG') != -1:
                name = ircmsg.split('!',1)[0][1:]
                sourceChannel = ircmsg.split('PRIVMSG',1)[1].split(':',1)[0].replace(' ', '')
                text = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]

                if (sourceChannel == botnick):
                    sourceChannel = name
                    if (name == adminname):
                        pass
                        #sendmsg("Hello, master.", "NWB")
                        #NOTE TO SELF: Add commands here, like "!leave [channel]" or "!join [channel]"

                # Leave 'channel' upon reading exit msg
                if (ircmsg.find(exitcode + ": " + botnick) != -1) and (name == adminname):
                    sendmsg("Gah! So you knew my weakness... I will retreat for now.", sourceChannel)
                    sendmsg("I have left " + sourceChannel + ".", "NWB")
                    partchan(sourceChannel)

                if ((sourceChannel == "#qa") and (server == "irc.sageru.org")):
                    maxTokens = 125
                    maxLines = 4
                elif ((sourceChannel == "#qa") and (server == "irc.rizon.net")):
                    maxTokens = 250
                    maxLines = 5
                elif (sourceChannel == "#chatgpt"):
                    maxTokens = 300
                    maxLines = 15
                else:
                    maxTokens = default_maxTokens
                    maxLines = default_maxLines

                parts = text.split()

                if len(parts) == 0:
		            parts.append("")

                messages = ""
                message = ""

                ############### Stable Diffusion Here #################
                #######################################################

                if (sd_status == True):
                    if ((parts[0].lower() == str("." + "sd")) or (parts[0].lower() == str("sd" + ",")) or (parts[0].lower() == str("sd" + ":"))):
                        #print("Stable Diffusion Matched")
                        
                        prompt = parts[1:]                
                        prompt = " ".join(prompt)

                        messages = stablediffusion.prompt(prompt)
                
                #######################################################
                #######################################################

                ###################### LLM API Here ######################
                #######################################################

                elif (llm_api_status == True):
                    if ((parts[0].lower() == str("." + "gpt3")) or (parts[0].lower() == str("gpt3" + ",")) or (parts[0].lower() == str("gpt3" + ":"))):
                        #print("GPT3 Matched")
                        
                        prompt = parts[1:]
                        prompt = " ".join(prompt)
                            
                        messages = gpt3.prompt(prompt, maxTokens, maxLines)
                
                #######################################################
                #######################################################

                ################### LLM Proxy Here ####################
                #######################################################

                elif (llm_proxy_status == True):
                    if ((parts[0].lower() == str("chatgpt" + ":")) or (parts[0].lower() == str("." + "chatgpt")) or (parts[0].lower() == str("chatgpt" + ",")) or (parts[0].lower() == str("gpt4" + ":")) or (parts[0].lower() == str("." + "gpt4")) or (parts[0].lower() == str("gpt4" + ",")) or (parts[0].lower() == str("gpt" + ":")) or (parts[0].lower() == str("." + "gpt")) or (parts[0].lower() == str("gpt" + ","))):
                        #print("GPT4 Matched")
                        
                        prompt = parts[1:]                
                        prompt = " ".join(prompt)
                        
                        name = ""
                        if (server == "irc.sageru.org"):
                            name = "15[GPT4]"
                        
                        messages = Bot_Commands.botCommands(sendmsg, chatgpt, name, prompt, maxTokens, maxLines, sourceChannel, server)
                        
                    elif ((parts[0].lower() == str("otaku-chan" + ":")) or (parts[0].lower() == str("!o")) or (parts[0].lower() == str("." + "otaku-chan")) or (parts[0].lower() == str("otaku-chan" + ",")) or (parts[0].lower() == str("otaku" + ":")) or (parts[0].lower() == str("." + "otaku")) or (parts[0].lower() == str("otaku" + ","))):
                        #print("Otaku-chan Matched")
                        
                        prompt = parts[1:]                
                        prompt = " ".join(prompt)
                        
                        name = ""
                        if (server == "irc.sageru.org"):
                            name = "2[Otaku-chan]"

                        messages = Bot_Commands.botCommands(sendmsg, otakuchan, name, prompt, maxTokens, maxLines, sourceChannel, server)
                
                #######################################################
                #######################################################

                for i, message in enumerate(messages):
                    #print(message)
                    sendmsg(f"{message}", sourceChannel)
                    time.sleep(0.250)

                ################## Relay Mode Here ####################
                #######################################################

                # Relay Mode Here
                if (relayMode == True) and ((ircmsg.find('PRIVMSG ' + channel + " :") != -1) or (ircmsg.find('PRIVMSG ' + channel2 + " :") != -1)):
                    name = ircmsg.split('!',1)[0][1:]
                    message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
                    
                    if sourceChannel == channel:
                        destinationChannel = channel2
                    else:
                        destinationChannel = channel
                    
                    if(twowayRelay == False and sourceChannel == channel2):
                        message = ""
                    
                    if relayLocation == True:
                        message = "[" + sourceChannel + "]: " + message
                        
                    # Don't send messages that include "@ kissu.moe", this is to prevent message duplication from the URL title link bot. If the message does not contain this, send the message.
                    if (ircmsg.find('@ kissu.moe') == -1) and (message != ""): 
                        print("[Source:" + sourceChannel + "][Destination:" + destinationChannel + "]: " + message)
                        sendmsg(message, destinationChannel)
                
                #######################################################
                #######################################################

            else:
                if ircmsg.find("KICK") != -1: # Reconnect to channel on kick.
                    time.sleep(10)
                    print("KICK: " + ircmsg)
                    sourceChannel = ircmsg.split('KICK',1)[1].split(botnick + ' :',1)[0].replace(' ', '')
                    joinchan(sourceChannel)

                if ircmsg.find("PING") != -1: # Reply to PINGs.
                    nospoof = ircmsg.split(' ', 1)[1] # Unrealircd 'nospoof' compatibility.
                    ircsend("PONG " + nospoof)
                    if debugmode: # If debugmode is True, msgs will print to screen.
                        print("Replying with '"+ nospoof +"'")
                    lastpingreceived = time.time() # Set time of last PING.
                    if (time.time() - lastpingreceived) >= threshold: # If last PING was longer than set threshold, try and reconnect.
                        if debugmode: # If debugmode is True, msgs will print to screen.
                            print('PING time exceeded threshold')
                        connected = False
                        reconnect()
                
try: # Here is where we actually start the Bot.
    if not connected:
        connect() # Connect to server.
    
except KeyboardInterrupt: # Kill Bot from CLI using CTRL+C
    ircsend("QUIT Terminated Bot using [ctrl + c]")
    if debugmode: # If debugmode is True, msgs will print to screen.
        print('... Terminated Bot using [ctrl + c], Shutting down!')
    sys.exit()
    
