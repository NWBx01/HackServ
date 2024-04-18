#!/usr/bin/env python3
#
# HackServ IRC Bot - Config File
# hsConfig.py
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
#
config_version = 1.2
import random
import time
from requests import get
ip = get('https://api.ipify.org').text
#################################################
############# Booleans ##########################
debugmode = True # If True, all print msgs will be active. (use False if you want to run in the background)
onJoin = False # If True, the bots onJoin actions will be enabled.
usessl = False # Connect using SSL. (True or False)
selfSignedCerts = False # Allow self-signed certs or not. Not recommended unless you trust the host, as packets can not be verified as authentic.
useservpass = False # Use a password to connect to IRC Server. (True or False)
usesasl = False # Authenticate using SASL. (True or False)
enableshell = False # Enable Shell commands. (True or False)
starttime = time.time()

#################################################
############# Bot Settings ######################
server = "irc.sageru.org" # Server to connect to.
port = 6667 # Port to connect to. SSL port is typically 6697, and non-SSL 6667
serverpass = "password" # Password for IRC Server. (UnrealIRCD uses this as default NickServ ident method)

# There's no real limit on the number of channels to relay to or from. For example, you could do something like relay messages from one channel and send it to 3 others, or do the reverse: relay messages from 3 channels into a single channel.
channel = "#qa" # Channel to relay messages from.
channel2 = "#chatgpt" # Channel to relay messages to. 

#botnick = "botnick" # Your bots IRC nick.
#botnick = "ip" + ip.replace(".", "_") # Set bots nick to IP address, but in proper IRC nick compatible format.
#botnick = "hs["+ str(random.randint(10000,99999)) +"]" # Set bots IRC Nick to 'hs' + 5 random numbers.
botnick = "Otaku-chan" # Set this to the type of bot running. i.e. "stable_diffusion_bot", and so forth.
nspass = "PdRA9seSTnveK9Shm9oP" # Bots NickServ password.
nickserv = "NickServ" # Nickname service name. (sometimes it's differnet on some networks.)
adminname = "NWB" # Bot Master's IRC nick.
exitcode = "DeathFlag" # Command 'exitcode + botnick' is used to kill the bot.
#################################################
#################################################


#################################################
############## Optional Modes ###################

relayMode = False # If relay mode is set to 'True', messages are relayed from channel to channel2. Otherwise, both channels are treated normally.
relayLocation = False # If relay location is set to 'True', messages will show where they came from, such as "[#qa]: Hello"
twowayRelay = False # If two-way relay is set to 'True', messages will be sent to and from both channels.

sd_status = False # Allows Stable Diffusion requests
   
llm_api_status = False # Allows requests via an LLM API, such as OpenAI.

llm_proxy_status = True # Allows requests via an LLM Proxy Service

otakuchan_status = True # Allows Otaku-chan (ChatGPT) requests

default_maxTokens = 256 # Max tokens when making an LLM Prompt
default_maxLines = 5 # Max lines to return
#################################################
#################################################


#################################################
############# ChatGPT Settings ##################
#These settings are for using the browser version of ChatGPT. This current is non-functional because ChatGPT has switched to using web sockets, so for all intents and purposes this is depreciated functionality.

auth_token =""

cookie_csrf = ""
cookie_cfuvid = ""
cookie_callback = ""
cookie_cfbm = ""
cookie_cfclearance = ""
cookie_auth = ""

cookieFinal = "__Host-next-auth.csrf-token=" + cookie_csrf + "; " + "_cfuvid=" + cookie_cfuvid + "; " + "__Secure-next-auth.callback-url=" + cookie_callback + "; " + "__cf_bm=" + cookie_cfbm + "; " + "cf_clearance=" + cookie_cfclearance + "; " + "__Secure-next-auth.session-token=" + cookie_auth



cookieFinal = ""


useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
#################################################
#################################################