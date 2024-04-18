from hsConfig import *
if (llm_api_status == True):
    from llm_api import * # import the llm_api.py file. 
if (llm_proxy_status == True):
    from llm_proxy import *# import the llm_proxy.py file. NOTE: Requires SillyTavern to be running
if (sd_status == True):
    from stablediffusion import * # import the stablediffusion.py file. NOTE: Requires AUTOMATIC1111's Stable Diffusion Web UI to be running

from utilities import download
import time
import pathlib
from pathlib import Path

############# Bot Initialization Here #################
#######################################################

class Bot_Commands:
    def __init__(self):
        self.generator = LLM_Proxy()

    def botCommands(sendmsg, botObject, name, prompt, maxTokens, maxLines, sourceChannel, server):
        #print("Checking for Bot Command")
        message = ""
        messages = []
        
        if (prompt.lower() == ""):
            if (server == "irc.sageru.org"):
                name = name + ": "
            message = name + "7You did not attach a prompt..."
            messages.append(message)

            return messages

        elif (prompt.lower() == "!reset"):
            #print("Bot Command: " + name + " Reset")
            botObject.prompt(sendmsg, name, prompt, maxTokens, maxLines, "", "reset", sourceChannel, server)

            if (name == "2[Otaku-chan]"):
                message = "7Otaku-chan's memory has been wiped."
            elif (name == "15[GPT4]"):
                message = "7GPT4's memory has been wiped."
                
            messages.append(message)
            
            if (botObject.returnTokens() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Token Display: " + mode
            messages.append(message)
            
            if (botObject.returnModel() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Model Display: " + mode
            messages.append(message)

            if (botObject.returnDebug() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Debug Display: " + mode
            messages.append(message)

            return messages
            
        
    
        elif (prompt.lower() == "!tokens"):
            #print("Bot Command: " + name + " Tokens")
            botObject.toggleTokens()
            
            if (botObject.returnTokens() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Token Display: " + mode
            messages.append(message)

            return messages
            
        elif (prompt.lower() == "!model"):
            #print("Bot Command: " + name + " Model")
            botObject.toggleModel()
            
            if (botObject.returnModel() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Model Display: " + mode
            messages.append(message)

            return messages
            
        elif (prompt.lower() == "!debug"):
            #print("Bot Command: " + name + " Debug")
            botObject.toggleDebug()
            
            if (botObject.returnDebug() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Debug Display: " + mode
            messages.append(message)
            
            if (botObject.returnModel() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Model Display: " + mode
            messages.append(message)
            
            if (botObject.returnTokens() == True):
                mode = "3Enabled"
            else:
                mode = "4Disabled"
            
            message = "Token Display: " + mode
            messages.append(message)

            return messages
        
        elif (prompt.lower() == "!undo"):
            #print("Bot Command: " + name + " Undo")
            botObject.prompt(sendmsg, name, prompt, maxTokens, maxLines, "", "undo", sourceChannel, server)
            if (server == "irc.sageru.org"):
                name = name + ": "
            message = name + "7Previous two messages deleted"
            messages.append(message)

            return messages
        
        elif ((prompt.lower() == "!regen") or (prompt.lower() == "!regenerate")):
            #print("Bot Command: " + name + " Regen")

            messages = botObject.prompt(sendmsg, name, "", maxTokens, maxLines, "", "regen", sourceChannel, server)

            for message in messages:
                print(message)

            if (server == "irc.sageru.org"):
                name = name + ": "
            message = name + "7Regenerating last message"
            messages.insert(0, message)

            return messages
        
        elif ((prompt.lower() == "!continue") or (prompt.lower() == "!cont")):
            #print("Bot Command: " + name + " Continue")

            messages = botObject.prompt(sendmsg, name, "", maxTokens, maxLines, "", "continue", sourceChannel, server)

            if (server == "irc.sageru.org"):
                name = name + ": "
            message = name + "7Continuing last message"
            messages.insert(0, message)

            return messages
        
        elif ((prompt.lower() == "!resume")):
            #print("Bot Command: " + name + " Resume")
            messages = botObject.returnTruncatedPrompt()
            if messages == "":
                messages = []
                if (server == "irc.sageru.org"):
                    name = name + ": "
                message = name + "7No message to resume"
                messages.append(message)

            else:
                botObject.setTruncatedPrompt("")
                if (server == "irc.sageru.org"):
                    name = name + ": "
                message = name + "7Resuming last message"
                messages.insert(0, message)

            return messages
        
        elif (prompt.lower().find('!image') != -1):
            #print("Bot Command: " + name + " Image")
            if (server != "irc.rizon.net") and (server != "irc.sageru.org"):
                if (server == "irc.sageru.org"):
                    message = name + ": 7Sending images is only supported in #chatgpt at the moment"
                else:
                    message = name + "7Sending images is only supported in #chatgpt at the moment"
                messages.append(message)
            else:
                dlURL = ""
                dlMessage = ""
                dlFile = ""
                
                if prompt.find(' ') != -1:
                    prompt = prompt.split(' ', 1)[1]
                    try:
                        dlMessage = prompt.split(' ', 1)[1]
                    except:
                        dlMessage = ""
                    try:
                        dlURL = prompt.split(' ')[0]
                    except:
                        dlURL = prompt
                    filename = dlURL.split('/')[-1]
                    extension = dlURL.split('.')[-1]
                    
                    #print("EXTENSION: " + extension)
                    
                    extension = extension.lower()
                    
                    if ((extension == "png") or (extension == "jpeg") or (extension == "jpg") or (extension == "webp") or (extension == "gif")):
                        try:
                            dlFile = Path.joinpath(Path.cwd(), Path(r"Downloads\\" + filename))
                            status = download(dlURL, dlFile)
                            if (botObject.returnDebug() == True):
                                print(dlFile)
                            if (status) == "OK":
                                messages = botObject.prompt(sendmsg, name, dlMessage, maxTokens, maxLines, dlFile, "", sourceChannel, server)
                            
                                #if os.path.exists(dlFile):
                                #    if (botObject.returnDebug() == True):
                                #        print("File Deleted")
                                #    time.sleep(5)
                                #    os.remove(dlFile)
                            
                            else:
                                if (server == "irc.sageru.org"):
                                    name = name + ": "
                                message = name + "7" + status
                                messages.append(message)
                        except:
                            if (server == "irc.sageru.org"):
                                name = name + ": "
                            message = name + "7Unable to download file"
                            messages.append(message)
                    else:
                        if (server == "irc.sageru.org"):
                            name = name + ": "
                        message = name + "7Unsupported filetype. (Supported Filetypes are: PNG, JPEG, JPG, WEBP, and GIF (non-animated))"
                        messages.append(message)

                else:
                    if (server == "irc.sageru.org"):
                        name = name + ": "
                    message = name + "7Could not parse. The command should be in the format of 'otaku: !image [URL] [message]' to work properly."
                    messages.append(message)
            
            return messages
            
        
        elif ((prompt.lower() == "!help") or (prompt.lower() == "!commands")):
            #print("Bot Command: " + name + " Help")
            if (server == "irc.sageru.org"):
                name = name + ": "
            else:
                name = ""
            messages.append(name + "7The following is a list of commands and their descriptions:")
            messages.append("7!help - Show this help screen")
            messages.append("7!image [URL] [message] - Sends an image")
            messages.append("7!system [message] - Sends a system message")
            messages.append("7!continue - Continues generating the last response from where it ended")
            messages.append("7!resume - Displays the last response, beginning from where it was truncated")
            messages.append("7!regen - Regenerate the last response")
            messages.append("7!undo - Undos the previous two messages")
            messages.append("7!reset - Creates a new chat and resets options")
            messages.append("7!tokens - Shows token context size utilization")
            messages.append("7!model - Shows the model being used to generate a response")
            messages.append("7!debug - Show additional debug information")
            messages.append("7!uptime - Show uptime")

            return messages
        
        elif ((prompt.lower().find('!sys') != -1) or (prompt.lower().find('!system') != -1)):
            #print("Bot Command: " + name + " System Message")
            if prompt.find(' ') != -1:
                prompt = prompt.split(' ', 1)[1]
            botObject.prompt(sendmsg, name, prompt, maxTokens, maxLines, "", "system", sourceChannel, server)
            if (server == "irc.sageru.org"):
                name = name + ": "
            message = name + "7Added System message"
            messages.append(message)

            return messages
        
        elif ((prompt.lower() == "!uptime")):
            #print("Bot Command: " + name + " Uptime")
            message = "7Uptime: "
            if (server == "irc.sageru.org"):
                name = name + ": "

            uptime = time.time() - starttime
            seconds = uptime

            years = int(seconds / (365*24*60*60))
            if (years != 0):
                message += str(years) + " year"
                if years != 1:
                    message += "s"
                message += ", "

            seconds -= years * (365*24*60*60)

            months = int(seconds / (30*24*60*60))
            if (months != 0):
                message += str(months) + " month"
                if months != 1:
                    message += "s"
                message += ", "

            seconds -= months * (30*24*60*60)

            days = int(seconds / (24*60*60))
            if (days != 0):
                message += str(days) + " day"
                if days != 1:
                    message += "s"
                message += ", "

            seconds -= days * (24*60*60)

            hours = int(seconds / (60*60))
            if (hours != 0):
                message += str(hours) + " hour"
                if hours != 1:
                    message += "s"
                message += ", "

            seconds -= hours * (60*60)

            minutes = int(seconds / 60)
            if (minutes != 0):
                message += str(minutes) + " minute"
                if minutes != 1:
                    message += "s"
                message += ", "

            seconds -= minutes * 60

            if (seconds != 0):
                message += str(int(seconds)) + " second"
                if seconds != 1:
                    message += "s"

            messages = []
            messages.append(name + message)

            return messages

        else:
            #print("Bot Command: " + name + " Message")
            messages = botObject.prompt(sendmsg, name, prompt, maxTokens, maxLines, "", "", sourceChannel, server)

            return messages