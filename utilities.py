from hsConfig import *
import shutil
import urllib.request
import urllib.parse
import requests

################ Utility Stuff Here ###################
#######################################################

# Downloads a file from a given URL, to a particular filepath with filename.
# Doesn't work with sites that issue a cloudflare cookie
def download(url, file): 
    print("Downloadin'")
    if ((url.find('http://') == -1) and (url.find('https://') == -1)):
        url = "https://" + url
    referalURL = "https://" + url.split('/')[2] + "/"
    
    headers = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    'Accept-Encoding': "gzip, deflate, br",
    'Accept-Language': "en-US,en;q=0.5",
    'Cache-Control': "no-cache",
    'Connection': "keep-alive",
    'Referer': referalURL,
    'DNT': 1,
    'Pragma': "no-cache",
    'Sec-Fetch-Dest': "image",
    'Sec-Fetch-Mode': "no-cors",
    'Sec-Fetch-Site': "same-site",
    'User-Agent': useragent
    }

    #urllib.request.urlretrieve(str(url), str(file))
    request = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(url) as response, open(file, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        return "OK"
    except urllib.error.URLError as e:
        return f"Failed to download the file. Error: {e}"
    except urllib.error.HTTPError as e:
        return f"HTTP error occurred while downloading the file. Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def parse_outgoing(message_prefix, message, maxLines, server):
    #Text = light purple 13
    #Actions = light green 9
    #Quotes = orange 7
    
    #message = message_prefix + "13 " + message
    
    total_tildes = message.count('~')
    total_underscores = message.count('_')
    total_asterisks = message.count('*')
    total_asterisks = message.count('*')
    total_quotes = message.count("\"") + message.count("“") + message.count("”") + message.count("„") + message.count("«") + message.count("»") + message.count("‹") + message.count("›") +  message.count("《") + message.count("》") + message.count("〈") + message.count("〉") + message.count("⟪") + message.count("⟫") + message.count("⟨") + message.count("⟩") + message.count("「") + message.count("」") + message.count("『") + message.count("』")
    
    message = message.replace("\\\"", "\"")
    message = message.replace("\\\'", "\'")
    message = message.replace("\\n", "\n")
    lines = message.split("\n")

    messages = []
    tempLines = []
    
    truncated_prompt = [] # This is for messages that extend past the maximum amount of lines and get truncated.
    truncated = False
    
    # Remove lines that are blank, this ensures that len(lines) returns the actual number of printable lines.
    for line in lines:
        if (line != ""):
            tempLines.append(line)
    
    lines = tempLines
    
    if (server == "irc.sageru.org"):
        maxCharsPerLine = 500
    elif (server == "irc.rizon.net"):
        maxCharsPerLine = 450

    lineCounter = 0
    for line in lines:
        if (lineCounter < maxLines):
            words = line.split(" ")
            
            if (lineCounter > 0):
                current_message = "13"
            else:
                current_message = message_prefix + "13 "
            
            asterisk_count = 0 #Replace pairs of asterisks (*) with IRC formatting characters
            quote_count = 0
            underscore_count = 0
            tilde_count = 0
            word_index = 0
            message_appended = False
            # Loops for the number of times necessary to break a line into multiples and correctly appends next messages where the last line ended
            for i in range((len(line) + maxCharsPerLine - 1) // maxCharsPerLine):        
                while word_index < len(words):
                    if (lineCounter >= maxLines):
                        truncated = True
                        lineCounter = 0
                    
                    reconstructedWord = ""
                    for letter in words[word_index]:
                        #Strikethrough; Red
                        if letter == "~":
                            if (total_tildes > 1):
                                tilde_count += 1

                                if words[word_index + 1] == "~":
                                    if (tilde_count == 1):
                                        reconstructedWord += chr(0x1E) + "4" + letter 
                                    else:
                                        reconstructedWord += letter + "13"
                                        tilde_count = 0

                        #Underline; Light blue
                        if letter == "_":
                            if (total_underscores > 1):
                                underscore_count += 1

                                if words[word_index + 1] == "_":
                                    if (underscore_count == 1):
                                        reconstructedWord += chr(0x1F) + "2" + letter 
                                    else:
                                        reconstructedWord += letter + "13"
                                        underscore_count = 0

                        #Bold; Dark Purple
                        #Italics; Light green
                        if letter == "*":
                            if (total_asterisks > 1):
                                asterisk_count += 1

                                if words[word_index + 1] == "*":
                                    if (asterisk_count == 1):
                                        reconstructedWord += chr(0x02) + "6" + letter 
                                    else:
                                        reconstructedWord += letter + "13"
                                        asterisk_count = 0
                                else:
                                    if (asterisk_count == 1):
                                        reconstructedWord += chr(0x1D) + "9" + letter
                                    else:
                                        reconstructedWord += letter + "13"
                                        asterisk_count = 0

                        #Quotes; Orange
                        elif ((letter == "\"") or (letter == "“") or (letter == "”") or (letter == "„") or (letter == "«") or (letter == "»") or (letter == "‹") or (letter == "›") or  (letter == "《") or (letter == "》") or (letter == "〈") or (letter == "〉") or (letter == "⟪") or (letter == "⟫") or (letter == "⟨") or (letter == "⟩") or (letter == "「") or (letter == "」") or (letter == "『") or (letter == "』")):
                            if (total_quotes > 1):
                                quote_count += 1
                                
                                if (quote_count == 1):
                                    reconstructedWord += "7" + letter
                                else:
                                    reconstructedWord += letter + "13"
                                    quote_count = 0
                        else:
                            reconstructedWord += letter
                    
                    if (len(current_message) + len(reconstructedWord) + 1 <= maxCharsPerLine):
                        current_message += reconstructedWord + " "
                        word_index += 1
                    else:
                        if (truncated == False):
                            messages.append(current_message)
                        else:
                            truncated_prompt.append(current_message)
                        message_appended = True
                        lineCounter += 1
                        if asterisk_count == 1:
                            current_message = chr(0x1D) + "9"
                        elif quote_count == 1:
                            current_message = "7"
                        else:
                            current_message = "13"
                        #break
                        
                    if (word_index == len(words)):
                        if (truncated == False):
                            messages.append(current_message)
                        else:
                            truncated_prompt.append(current_message)
                        lineCounter += 1
                        message_appended = True
                
                if (lineCounter >= maxLines):
                    truncated = True
                    lineCounter = 0
                
                elif not message_appended:
                    if (truncated == False):
                        messages.append(current_message)
                    else:
                        truncated_prompt.append(current_message)
                    lineCounter += 1

            if (lineCounter >= maxLines):
                truncated = True
                lineCounter = 0
    
    if (truncated == True) and (truncated_prompt != []) and (str(truncated_prompt) != "") and (str(truncated_prompt) != "13") and (str(truncated_prompt) != "7") and (str(truncated_prompt) != chr(0x1D) + "14"):
        messages.append("7Too many lines! Stopping. Use !resume to continue response.")
        
    return [messages, truncated_prompt]

def WaitTimeInSeconds(waitTime):    
    minutes = 0
    seconds = 0
    waitTime = waitTime.replace("min", "")
    waitTime = waitTime.replace("sec", "")
    
    if (waitTime == "no wait"):
        return 0
    else:
        #Example: 3min, 53sec
        if (waitTime.find(', ') != -1):
            waitTime = waitTime.split(', ')
            minutes = int(waitTime[0])
            seconds = int(waitTime[1])
            
            return (minutes * 60 + seconds)
        else:
            seconds = int(waitTime)
            return seconds

def litterboxUpload(filepath):
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    data = {'time': '12h', 'reqtype': 'fileupload'}
    files = {'fileToUpload': open(filepath,'rb')}
    
    query = requests.post(url=url, data=data, files=files)
    response = query.text
    
    response = response.split("\n")[0]
    
    #print(response)
    
    return response
            
def x0atUpload(filepath):
    url = "https://x0.at/"
    files = {'file': open(filepath,'rb')}
    
    query = requests.post(url=url, files=files)
    response = query.text
    
    response = response.split("\n")[0]
    
    #print(response)
    
    return response