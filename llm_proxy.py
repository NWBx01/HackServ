from utilities import *
from api_keys import *

import time
import requests
import urllib.request
import urllib.parse
import json
from playwright.sync_api import sync_playwright
from cf_clearance import sync_cf_retry, sync_stealth

################ LLM Proxy Stuff Here #################
#######################################################

class LLM_Proxy:
    def __init__(self):
        self.token_status = False
        self.model_status = True
        self.debug_status = False
        self.start_time = 0
        self.long_response_threshold = 45
        self.long_response_message = False
        self.truncated_prompt = ""
        
    def returnTokens(self):
        return self.token_status
        
    def toggleTokens(self):
        if self.token_status == False:
            self.token_status = True
        else:
            self.token_status = False
            
    def returnModel(self):
        return self.model_status
        
    def toggleModel(self):
        if self.model_status == False:
            self.model_status = True
        else:
            self.model_status = False

    def returnDebug(self):
        return self.debug_status
        
    def toggleDebug(self):
        if self.debug_status == False:
            self.debug_status = True
            self.model_status = True
            self.token_status = True
        else:
            self.debug_status = False
            self.model_status = False
            self.token_status = False
    
    def setStartTime(self):
        self.start_time = time.time()

    def returnStartTime(self):
        return self.start_time

    def returnLongResponseThreshold(self):
        return self.long_response_threshold

    def setLongResponseMessage(self, status):
        self.long_response_message = status

    def returnLongResponseMessage(self):
        return self.long_response_message

    def setTruncatedPrompt(self, truncated_prompt):
        self.truncated_prompt = truncated_prompt
    
    def returnTruncatedPrompt(self):
        return self.truncated_prompt

    def proxyPrompt(self, sendmsg, sourceChannel, browser, page, mode_select, endpoint_url, proxy_key, prompt_message, maxTokens, character_name, provider, model_name, model_short_name, model_full_name, model_wait_threshold, streaming_response, filePathUpload, special):
        encountered_error = False
        response_info = ""
        temp_response = ""
        alternative_message_save = False
        response_message = ""
        message_prefix = ""

        try:
            if (provider == "OpenAI"):
                model_color = "14" 
            if (provider == "Azure"):
                model_color = "10"
            if (provider == "AWS"):
                model_color = "7"
            if (provider == "Google"):
                model_color = "3"
            

            print("Trying " + model_full_name + " for a response")
            page.get_by_title("API Connections").click()
            if (mode_select == "custom"):
                page.locator("#chat_completion_source").select_option("custom")
                page.get_by_placeholder("Example: http://localhost:1234/v1").fill(endpoint_url)
                page.get_by_placeholder("✔️ Key saved").fill(proxy_key)
                page.locator("#api_button_openai").click(timeout=1500)

                try:
                    page.locator("#model_custom_select").select_option(model_name, timeout=1500)
                except:
                    page.get_by_placeholder("Example: gpt-3.5-turbo").click(timeout=1500)
                    page.get_by_placeholder("Example: gpt-3.5-turbo").fill(model_name, timeout=1500)
            elif (mode_select == "claude"):
                page.locator("#chat_completion_source").select_option("claude")
                page.locator("#openai_api > div > .inline-drawer-toggle > .fa-solid").click()
                if (endpoint_url == "https://" + primary_proxy_url + "/proxy/aws/claude"):
                    page.locator("#openai_proxy_preset").select_option("Primary Proxy AWS")
                elif (endpoint_url == "https://" + secondary_proxy_url + "/proxy/aws/claude"):
                    page.locator("#openai_proxy_preset").select_option("Secondary Proxy AWS")
                page.locator("#model_claude_select").select_option("claude-3-sonnet-20240229")
                
    
            page.get_by_title("API Connections").click()

            page.get_by_title("AI Response Configuration").click()
            page.locator("#openai_max_context_counter").fill(str(maxTokens))
            page.locator("#openai_max_tokens").press("Enter")
            if (streaming_response == True):
                page.get_by_role("checkbox", name="Streaming").check()
            else:
                page.get_by_role("checkbox", name="Streaming").uncheck()

            if (filePathUpload != ""):
                page.get_by_text("Send inline images").check()
            else:
                page.get_by_text("Send inline images").uncheck()

            if (mode_select == "claude"):
                if (character_name == "2[Otaku-chan]"):
                    page.get_by_placeholder("Start Claude's answer with...").fill("Sugoi writing, {{user}}! Now I'll reply as Otaku-chan, highlighting her personality and dislikes. Things directed towards me, I'll keep SFW and PG-13, but talking about NSFW otaku things is totally fine! With that in mind here's my reply: ")
                elif (character_name == "15[GPT4]"):
                    page.get_by_placeholder("Start Claude's answer with...").fill("")

            if (self.returnModel() == True):
                if (server == "irc.sageru.org"):
                    if (self.returnDebug() != True):
                        message_prefix =  "|" + model_color + "[" + model_short_name + "]"
                    else:
                        message_prefix =  "|" + model_color + "[" + provider + ": " + model_name + "]"
                else:
                    if (self.returnDebug() != True):
                        message_prefix =  model_color + model_short_name
                    else:
                        message_prefix =  model_color + "[" + provider + ": " + model_name + "]"
            try:
                with page.expect_response("http://127.0.0.1:8000/api/backends/chat-completions/generate", timeout=(model_wait_threshold * 1000)) as response_info:
                    if (special == "regen"):
                        page.locator("#options_button").click()
                        page.locator("#option_regenerate").click()
                    elif (special == "continue"):
                        page.locator("#options_button").click()
                        page.locator("#option_continue").click()
                    else:
                        page.get_by_title("Send a message").click()
                        
                    if (((time.time() - self.returnStartTime() ) >= self.returnLongResponseThreshold()) and (self.returnLongResponseMessage() == False)):
                        self.setLongResponseMessage(True)
                        sendmsg(irc_message + "7It's taking longer than usual to get a response", sourceChannel)

                    page.expect_response("http://127.0.0.1:8000/api/chats/save", timeout=(model_wait_threshold * 1000))
            except:
                encountered_error = True
                print("Timed out waiting for " + model_full_name)
                raise ValueError("Timed out waiting for " + model_full_name)
            try:
                temp_response = response_info
                temp_response = response_info.value
                temp_response = str(temp_response.json()) #json.dumps(response.json())
                
                # Check if the input is a list (indicating it has been split)
                if isinstance(temp_response, list):
                    # Join the list elements into a single string using the join method
                    temp_response = ''.join(temp_response)
                data_dict = eval(temp_response)
                try:
                    response_message = data_dict['choices'][0]['message']['content']
                except:
                    response_message = data_dict['error']['message']
            except:
                if (streaming_response == True):
                    alternative_message_save = True
                    page.locator(".mes.last_mes > .mes_block > .ch_name > .mes_buttons > .mes_edit").click()
                    response_message = page.locator("#curEditTextarea").input_value()
                    page.locator(".mes.last_mes > .mes_block > .ch_name > .mes_edit_buttons > .mes_edit_cancel").click()

            if (self.returnDebug() == True):
                print(model_full_name + " Response:\n" + str(response_message) + "\n")
            try:
                if (response_message.find('Proxy error') != -1):
                    encountered_error = True
                    print(model_full_name + " encountered a proxy Error")
        
                    page.locator("#options_button").click()
                    time.sleep(0.25)
                    page.locator("#option_delete_mes").click()
                    time.sleep(0.25)
                    page.locator('.mes.last_mes').click()
                    time.sleep(0.25)
                    page.locator("#dialogue_del_mes_ok").click()
                    time.sleep(0.25)
                    page.locator("#options_button").click()
                    time.sleep(0.25)
                    page.locator("#option_delete_mes").click()
                    time.sleep(0.25)
                    page.locator('.mes.last_mes').click()
                    time.sleep(0.25)
                    page.locator("#dialogue_del_mes_ok").click()
                    time.sleep(0.25)
                    
                    try:
                        page.get_by_placeholder("Type a message, or /? for help").click(timeout=1000)
                        page.get_by_placeholder("Type a message, or /? for help").fill(prompt_message) # Input the message

                        if (filePathUpload != ""):
                            page.get_by_title("Extras Extensions").click()
                            with page.expect_file_chooser() as fc_info:
                                page.get_by_text("Attach a File").click()
                            file_chooser = fc_info.value
                            file_chooser.set_files(filePathUpload)
                    except:
                        page.get_by_placeholder("Not connected to API!").click()
                        page.get_by_placeholder("Not connected to API!").fill(prompt_message) # Input the message

                        if (filePathUpload != ""):
                            page.get_by_title("Extras Extensions").click()
                            with page.expect_file_chooser() as fc_info:
                                page.get_by_text("Attach a File").click()
                            file_chooser = fc_info.value
                            file_chooser.set_files(filePathUpload)
                    
                    raise ValueError(model_full_name + " encountered a proxy error")
            
                elif (response_message.find('Reverse proxy error') != -1):
                    encountered_error = True
                    print("No keys available for " + model_full_name)
                    raise ValueError("No keys available for " + model_full_name)
                    
                elif (response_message.find('The response was filtered') != -1):
                    encountered_error = True
                    print(model_full_name + " response filtered")
                    raise ValueError(model_full_name + " response filtered")
            except:
                pass
            if (encountered_error == True):
                raise ValueError()
        except:
            encountered_error == True

        return_list = []
        return_list.append(encountered_error)
        return_list.append(response_info)
        return_list.append(temp_response)
        return_list.append(alternative_message_save)
        return_list.append(response_message)
        return_list.append(message_prefix)

        return return_list

    def prompt(self, sendmsg, name, message, maxTokensResponse, maxLines, filePathUpload, special, sourceChannel, server):
        print("Bot Prompting: " + name)
        self.setStartTime()
        self.setLongResponseMessage(False)
        #long_response_threshold = 55 # After X seconds, send a message noting it's taking a while to get a response.
        if (server == "irc.sageru.org"):
            irc_message = name + ": "
        else:
            irc_message = "" 
        
        response = ""
        original_response = ""
        message_prefix = ""
        response_info = ""
        temp_response = ""
        response_message = ""
        alternative_message_save = False
        data_dict = ""
        skip_all = False
        encountered_error = False
        maxTokensContext = 0 # This is the maximum amount of tokens the total prompt can be
        promptTokenUsage = 0 # This is the amount of tokens the prompt over all is using (includes total chat history)
        maxTokensResponse # This is the maximum amount of tokens an individual response can be
        tokenResponseUsage = 0 # This is the amount of tokens an individual response used            
        
        try:
            #raise ValueError("Primary Proxy Token Expired.")
            # Check the number of active keys and wait times for the models used.
            headers = {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            'Accept-Encoding': "",
            'Accept-Language': "en-US,en;q=0.5",
            'Alt-Used': primary_proxy_url,
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Cookie': "csrf=4d28e4e4310a078c53219a651b9104cfcd865bdea3dcaad16bdcb1dfabf0b6a1; connect.sid=s%3AaZbKvymEW6QclKHAR5GYwc10qGE96smL.IRph3RhWPvbOj5xFB4JibaisPluUg8ieQ3p1fEA14GA",
            'DNT': "1",
            'Host': primary_proxy_url,
            'Pragma': "no-cache",
            'Sec-Fetch-Dest': "document",
            'Sec-Fetch-Mode': "navigate",
            'Sec-Fetch-Site': "cross-site",
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
            }

            request = requests.get("https://" + primary_proxy_url, headers=headers)

            webpage = request.text

            webpage = webpage.split("<pre>")[1].split("</pre>")[0]

            primary_proxy_service_info = eval(webpage)

            if (self.returnDebug() == True):
                print("Webpage:\n\n" + request.text + "\n\n")

            proxy_key = primary_proxy_key

            openai_endpoint_url = primary_proxy_service_info['endpoints']['openai']
            try:
                openai_gpt4o_wait_time = WaitTimeInSeconds(primary_proxy_service_info['gpt4o']['estimatedQueueTime'])
                openai_gpt4o_keys = primary_proxy_service_info['gpt4o']['activeKeys']
            except:
                openai_gpt4o_wait_time = 0
                openai_gpt4o_keys = 0
            try:
                openai_gpt4_turbo_wait_time = WaitTimeInSeconds(primary_proxy_service_info['gpt4-turbo']['estimatedQueueTime'])
                openai_gpt4_turbo_keys = primary_proxy_service_info['gpt4-turbo']['activeKeys']
            except:
                openai_gpt4_turbo_wait_time = 0
                openai_gpt4_turbo_keys = 0
            try:
                openai_gpt4_32k_wait_time = WaitTimeInSeconds(primary_proxy_service_info['gpt4-32k']['estimatedQueueTime'])
                openai_gpt4_32k_keys = primary_proxy_service_info['gpt4-32k']['activeKeys']
            except:
                openai_gpt4_32k_wait_time = 0
                openai_gpt4_32k_keys = 0
            try:
                openai_gpt3_5_turbo_wait_time = WaitTimeInSeconds(primary_proxy_service_info['turbo']['estimatedQueueTime'])
                openai_gpt3_5_turbo_keys = primary_proxy_service_info['turbo']['activeKeys']
            except:
                openai_gpt3_5_turbo_wait_time = 0
                openai_gpt3_5_turbo_keys = 0

            aws_endpoint_url = primary_proxy_service_info['endpoints']['aws']
            try:
                aws_claude_sonnet_wait_time = WaitTimeInSeconds(primary_proxy_service_info['claude-opus']['estimatedQueueTime'])
                aws_claude_sonnet_keys  = primary_proxy_service_info['claude-opus']['activeKeys']
            except:
                aws_claude_sonnet_wait_time = 0
                aws_claude_sonnet_keys  = 0
            try:
                aws_claude_wait_time = WaitTimeInSeconds(primary_proxy_service_info['aws-claude']['estimatedQueueTime'])
                aws_claude_keys  = primary_proxy_service_info['aws-claude']['activeKeys']
            except:
                aws_claude_wait_time = 0
                aws_claude_keys  = 0

            azure_endpoint_url = primary_proxy_service_info['endpoints']['azure']
            try:
                azure_gpt4_turbo_wait_time = WaitTimeInSeconds(primary_proxy_service_info['azure-gpt4-turbo']['estimatedQueueTime'])
                azure_gpt4_turbo_keys = primary_proxy_service_info['azure-gpt4-turbo']['activeKeys']
            except:
                azure_gpt4_turbo_wait_time = 0
                azure_gpt4_turbo_keys = 0
            try:
                azure_gpt4_32k_wait_time = WaitTimeInSeconds(primary_proxy_service_info['azure-gpt4-32k']['estimatedQueueTime'])
                azure_gpt4_32k_keys = primary_proxy_service_info['azure-gpt4-32k']['activeKeys']
            except:
                azure_gpt4_32k_wait_time = 0
                azure_gpt4_32k_keys = 0
            
            google_endpoint_url = primary_proxy_service_info['endpoints']['google-ai']
            try:
                google_gemini_wait_time = WaitTimeInSeconds(primary_proxy_service_info['gemini-pro']['estimatedQueueTime'])
                google_gemini_keys  = primary_proxy_service_info['gemini-pro']['activeKeys']
            except:
                google_gemini_wait_time = 0
                google_gemini_keys  = 0
        except:
            print("Primary Proxy Down?")
            openai_gpt4o_wait_time = 0
            openai_gpt4o_keys = 0
            openai_gpt4_turbo_wait_time = 0
            openai_gpt4_turbo_keys = 0
            openai_gpt4_32k_wait_time = 0
            openai_gpt4_32k_keys = 0
            openai_gpt3_5_turbo_wait_time = 0
            openai_gpt3_5_turbo_keys = 0
            aws_claude_sonnet_wait_time = 0
            aws_claude_sonnet_keys = 0

            try:
                # Check the number of active keys and wait times for the models used.
                headers = {
                'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                'Accept-Encoding': "",
                'Accept-Language': "en-US,en;q=0.5",
                'Alt-Used': secondary_proxy_url,
                'Cache-Control': "no-cache",
                'Connection': "keep-alive",
                'Cookie': "connect.sid=s%3Ak9BzeJGz-EXOME9_rmYOsh5Q5or6-a9v.9LOKGnoWm5iplEJFi%2B5OdDWzpWfBa8ZyMqEbKQ5qTpY; csrf=071e55b6fe09560edb4f0c011681c93d4a5593c0611c15293298e3e4adf06eca",
                'DNT': "1",
                'Host': secondary_proxy_url,
                'Pragma': "no-cache",
                'Sec-Fetch-Dest': "document",
                'Sec-Fetch-Mode': "navigate",
                'Sec-Fetch-Site': "none",
                'Sec-Fetch-User': "?1",
                'Upgrade-Insecure-Requests': "1",
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
                }

                request = requests.get("https://" + secondary_proxy_url, headers=headers)

                webpage = request.text

                webpage = webpage.split("<pre>")[1].split("</pre>")[0]
                secondary_proxy_service_info = eval(webpage)
                
                if (self.returnDebug() == True):
                    print("Webpage:\n\n" + request.text + "\n\n")

                proxy_key = secondary_proxy_key

                aws_endpoint_url = secondary_proxy_service_info['endpoints']['aws']
                try:
                    aws_claude_sonnet_wait_time = WaitTimeInSeconds(secondary_proxy_service_info['aws-claude']['estimatedQueueTime'])
                    aws_claude_sonnet_keys = secondary_proxy_service_info['aws-claude']['sonnetKeys']
                except:
                    aws_claude_sonnet_wait_time = 0
                    aws_claude_sonnet_keys  = 0
                try:
                    aws_claude_wait_time = WaitTimeInSeconds(secondary_proxy_service_info['aws-claude']['estimatedQueueTime'])
                    aws_claude_keys = secondary_proxy_service_info['aws-claude']['activeKeys']
                except:
                    aws_claude_wait_time = 0
                    aws_claude_keys = 0

                azure_endpoint_url = secondary_proxy_service_info['endpoints']['azure']
                try:
                    azure_gpt4_turbo_wait_time = WaitTimeInSeconds(secondary_proxy_service_info['azure-gpt4-turbo']['estimatedQueueTime'])
                    azure_gpt4_turbo_keys = secondary_proxy_service_info['azure-gpt4-turbo']['activeKeys']
                except:
                    azure_gpt4_turbo_wait_time = 0
                    azure_gpt4_turbo_keys = 0
                try:
                    azure_gpt4_32k_wait_time = WaitTimeInSeconds(secondary_proxy_service_info['azure-gpt4-32k']['estimatedQueueTime'])
                    azure_gpt4_32k_keys = secondary_proxy_service_info['azure-gpt4-32k']['activeKeys']
                except:
                    azure_gpt4_32k_wait_time = 0
                    azure_gpt4_32k_keys = 0
                
                google_endpoint_url = secondary_proxy_service_info['endpoints']['google-ai']
                try:
                    google_gemini_wait_time = WaitTimeInSeconds(secondary_proxy_service_info['gemini-pro']['estimatedQueueTime'])
                    google_gemini_keys  = secondary_proxy_service_info['gemini-pro']['activeKeys']
                except:
                    google_gemini_wait_time = 0
                    google_gemini_keys  = 0
            except:
                print("Secondary Proxy Down?")
                azure_gpt4_turbo_wait_time = 0
                azure_gpt4_turbo_keys = 0
                aws_claude_wait_time = 0
                aws_claude_keys = 0
                azure_gpt4_32k_wait_time = 0
                azure_gpt4_32k_keys = 0
                google_gemini_wait_time = 0
                google_gemini_keys  = 0
                skip_all == True

        openai_gpt4o_streaming_response = False
        openai_gpt4_turbo_streaming_response = False
        azure_gpt4_turbo_streaming_response = False
        openai_gpt4_32k_streaming_response = False
        azure_gpt4_32k_streaming_response = False
        aws_claude_sonnet_streaming_response = False
        aws_claude_streaming_response = False
        openai_gpt3_5_turbo_streaming_response = False
        google_gemini_streaming_response = False
        
        print("OpenAI GPT-4o Wait Time: " + str(openai_gpt4o_wait_time))
        print("OpenAI GPT-4o Keys: " + str(openai_gpt4o_keys))
        print("OpenAI GPT-4-Turbo Wait Time: " + str(openai_gpt4_turbo_wait_time))
        print("OpenAI GPT-4-Turbo Keys: " + str(openai_gpt4_turbo_keys))
        print("Azure GPT-4-Turbo Wait Time: " + str(azure_gpt4_turbo_wait_time))
        print("Azure GPT-4-Turbo Keys: " + str(azure_gpt4_turbo_keys))
        print("OpenAI GPT-4-32K Wait Time: " + str(openai_gpt4_32k_wait_time))
        print("OpenAI GPT-4-32K Keys: " + str(openai_gpt4_32k_keys))
        print("Azure GPT-4-32K Wait Time: " + str(azure_gpt4_32k_wait_time))
        print("Azure GPT-4-32K Keys: " + str(azure_gpt4_32k_keys))
        print("AWS Claude Sonnet Wait Time: " + str(aws_claude_sonnet_wait_time))
        print("AWS Claude Sonnet Keys: " + str(aws_claude_sonnet_keys ))
        print("AWS Claude 2.1 Wait Time: " + str(aws_claude_wait_time))
        print("AWS Claude 2.1 Keys: " + str(aws_claude_keys ))
        print("OpenAI GPT-3.5-Turbo Wait Time: " + str(openai_gpt3_5_turbo_wait_time))
        print("OpenAI GPT-3.5-Turbo Keys: " + str(openai_gpt3_5_turbo_keys))
        print("Google Gemini Wait Time: " + str(google_gemini_wait_time))
        print("Google Gemini Keys: " + str(google_gemini_keys ))
        
        openai_gpt4_turbo_wait_threshold = 120 # Average wait ~20 seconds
        azure_gpt4_turbo_wait_threshold = 120 # Average wait ~20 seconds
        openai_gpt4_32k_wait_threshold = 60 # Average wait ~20 seconds
        azure_gpt4_32k_wait_threshold = 60 # Average wait ~20 seconds
        aws_claude_sonnet_wait_threshold = 90 # Average wait ~40 seconds
        aws_claude_wait_threshold = 90 # Average wait ~40 seconds
        openai_gpt3_5_turbo_wait_threshold = 60 # Average wait ~20 seconds
        google_gemini_wait_threshold = 90 # Average wait ~40 seconds
        
        openai_gpt4_turbo_skip_reason = ""
        azure_gpt4_turbo_skip_reason = ""
        openai_gpt4_32k_skip_reason = ""
        azure_gpt4_32k_skip_reason = ""
        aws_claude_sonnet_skip_reason = ""
        aws_claude_skip_reason = ""
        openai_gpt3_5_turbo_skip_reason = ""
        google_gemini_skip_reason = ""

        if ((filePathUpload == "") and (skip_all == False)):
            openai_gpt4o_skip = False
            openai_gpt4_turbo_skip = False
            azure_gpt4_turbo_skip = False
            openai_gpt4_32k_skip = False
            azure_gpt4_32k_skip = False
            aws_claude_sonnet_skip = False
            aws_claude_skip = False
            openai_gpt3_5_turbo_skip = False
            google_gemini_skip = False
        elif ((filePathUpload != "") and (skip_all == False)):
            openai_gpt4o_skip = False
            openai_gpt4_turbo_skip = False
            azure_gpt4_turbo_skip = False
            openai_gpt4_32k_skip = True
            openai_gpt4_32k_keys = 0
            azure_gpt4_32k_skip = True
            azure_gpt4_32k_keys = 0
            aws_claude_sonnet_skip = False
            aws_claude_skip = True
            aws_claude_keys = 0
            openai_gpt3_5_turbo_skip = True
            openai_gpt3_5_turbo_keys = 0
            google_gemini_skip = True
            google_gemini_keys = 0

            aws_claude_sonnet_wait_threshold = 1000

            openai_gpt4o_skip_reason = ""
            openai_gpt4_turbo_skip_reason = ""
            openai_gpt4_32k_skip_reason = "OpenAI GPT-4-32K does not support image uploads."
            azure_gpt4_32k_skip_reason = "Azure GPT-4-32K does not support image uploads."
            aws_claude_sonnet_skip_reason = ""
            aws_claude_skip_reason = "AWS Cluade 2.1 does not support image uploads."
            openai_gpt3_5_turbo_skip_reason = "Azure GPT-3.5-16K does not support image uploads."
            google_gemini_skip_reason = "Google Gemini does not support image uploads."

        # Checks in descending order whether there are any keys for our fallbacks. Naturally, we want a response, even if it's going to take a while. So, if there are no available keys for the last fallback, the timeout threshold for the last model, should be as long as possible in order to ensure we get a response.
        if (google_gemini_keys == 0):
            google_gemini_skip = True
            google_gemini_skip_reason = "Google Gemini has no available keys"
            openai_gpt3_5_turbo_wait_threshold = 1000
        if (openai_gpt3_5_turbo_keys == 0):
            openai_gpt3_5_turbo_skip = True
            openai_gpt3_5_turbo_skip_reason = "OpenAI GPT-3.5-Turbo has no available keys"
            aws_claude_wait_threshold = 1000
        if (aws_claude_keys == 0):
            aws_claude_skip = True
            aws_claude_skip_reason = "AWS Claude 2.1 has no available keys"
            aws_claude_sonnet_wait_threshold = 1000
        if (aws_claude_sonnet_keys == 0):
            aws_claude_sonnet_skip = True
            aws_claude_sonnet_skip_reason = "AWS Claude Sonnet has no available keys"
            azure_gpt4_32k_wait_threshold = 1000
        if (azure_gpt4_32k_keys == 0):
            azure_gpt4_32k_skip = True
            azure_gpt4_32k_skip_reason = "Azure GPT-4-32K has no available keys"
            openai_gpt4_32k_wait_threshold = 1000
        if (openai_gpt4_32k_keys == 0):
            openai_gpt4_32k_skip = True
            openai_gpt4_32k_skip_reason = "OpenAI GPT-4-32K has no available keys"
            azure_gpt4_32k_wait_threshold = 1000
        if (azure_gpt4_turbo_keys == 0):
            azure_gpt4_turbo_skip = True
            azure_gpt4_turbo_skip_reason = "Azure GPT-4-Turbo has no available keys"
            openai_gpt4_turbo_wait_threshold = 1000
        if (openai_gpt4_turbo_keys == 0):
            openai_gpt4_turbo_skip = True
            openai_gpt4_turbo_skip_reason = "OpenAI GPT-4-Turbo has no available keys"
            openai_gpt4o_wait_threshold = 1000
        if (openai_gpt4o_keys == 0):
            openai_gpt4o_skip = True
            openai_gpt4o_skip_reason = "OpenAI GPT-4o has no available keys"

        # Check if there are any issues with the model. If so, set a flag to skip it.
        # This is particularly important if there is an excessively long wait time. If we had not skipped the model and merely aborted it due to timeout, we would still be queued for that prompt
        # Meaning, we would be required to still wait the excessive wait time, regardless. Skipping the model entirely means we can skip this wait and just try a different model.
        # If there's no keys available, then we should obviously skip the model.
        
        if (openai_gpt4o_wait_time > openai_gpt4o_wait_threshold):
            openai_gpt4o_skip = True
            openai_gpt4o_skip_reason = "OpenAI GPT-4-Turbo wait time (" + str(openai_gpt4o_wait_time) + ") greater than wait threshold (" + str(openai_gpt4o_wait_threshold) + ")"
        else:
            openai_gpt4o_wait_threshold += openai_gpt4o_wait_time

        if (openai_gpt4_turbo_wait_time > openai_gpt4_turbo_wait_threshold):
            openai_gpt4_turbo_skip = True
            openai_gpt4_turbo_skip_reason = "OpenAI GPT-4-Turbo wait time (" + str(openai_gpt4_turbo_wait_time) + ") greater than wait threshold (" + str(openai_gpt4_turbo_wait_threshold) + ")"
        else:
            openai_gpt4_turbo_wait_threshold += openai_gpt4_turbo_wait_time

        if (azure_gpt4_turbo_wait_time > azure_gpt4_turbo_wait_threshold):
            azure_gpt4_turbo_skip = True
            azure_gpt4_turbo_skip_reason = "Azure GPT-4-Turbo wait time (" + str(azure_gpt4_turbo_wait_time) + ") greater than wait threshold (" + str(azure_gpt4_turbo_wait_threshold) + ")"
        else:
            azure_gpt4_turbo_wait_threshold += azure_gpt4_turbo_wait_time

        if (openai_gpt4_32k_wait_time > openai_gpt4_32k_wait_threshold):
            openai_gpt4_32k_skip = True
            openai_gpt4_32k_skip_reason = "OpenAI GPT4-32K wait time (" + str(openai_gpt4_32k_wait_time) + ") greater than wait threshold (" + str(openai_gpt4_32k_wait_threshold) + ")"
        else:
            openai_gpt4_32k_wait_threshold += openai_gpt4_32k_wait_time

        if (azure_gpt4_32k_wait_time > azure_gpt4_32k_wait_threshold):
            azure_gpt4_32k_skip = True
            azure_gpt4_32k_skip_reason = "Azure GPT4-32K wait time (" + str(azure_gpt4_32k_wait_time) + ") greater than wait threshold (" + str(azure_gpt4_32k_wait_threshold) + ")"
        else:
            azure_gpt4_32k_wait_threshold += azure_gpt4_32k_wait_time
          
        if (aws_claude_sonnet_wait_time > aws_claude_sonnet_wait_threshold): 
            aws_claude_sonnet_skip = True
            aws_claude_sonnet_skip_reason = "AWS Claude Sonnet wait time (" + str(aws_claude_sonnet_wait_time) + ") greater than wait threshold (" + str(aws_claude_sonnet_wait_threshold) + ")"
        else:
            aws_claude_sonnet_wait_threshold += aws_claude_sonnet_wait_time

        if (aws_claude_wait_time > aws_claude_wait_threshold): 
            aws_claude_skip = True
            aws_claude_skip_reason = "AWS Claude 2.1 wait time (" + str(aws_claude_wait_time) + ") greater than wait threshold (" + str(aws_claude_wait_threshold) + ")"
        else:
            aws_claude_wait_threshold += aws_claude_wait_time

        if (openai_gpt3_5_turbo_wait_time > openai_gpt3_5_turbo_wait_threshold):
            openai_gpt3_5_turbo_skip = True
            openai_gpt3_5_turbo_skip_reason = "OpenAI GPT3.5-16K wait time (" + str(openai_gpt3_5_turbo_wait_time) + ") greater than wait threshold (" + str(openai_gpt3_5_turbo_wait_threshold) + ")"
        else:
            openai_gpt3_5_turbo_wait_threshold += openai_gpt3_5_turbo_wait_time

        if (google_gemini_wait_time > google_gemini_wait_threshold):
            google_gemini_skip = True
            google_gemini_skip_reason = "Google Gemini wait time (" + str(google_gemini_wait_time) + ") greater than wait threshold (" + str(google_gemini_wait_threshold) + ")"
        else:
            google_gemini_wait_threshold += google_gemini_wait_time

           
        if (skip_all or ((openai_gpt4o_skip == True) and (openai_gpt4_turbo_skip == True) and (azure_gpt4_turbo_skip == True) and (openai_gpt4_32k_skip == True) and (azure_gpt4_32k_skip == True) and (aws_claude_sonnet_skip == True) and (aws_claude_skip == True) and (openai_gpt3_5_turbo_skip == True) and (google_gemini_skip == True))):
            print("Skip all. No keys available.")
            skip_all = True
            
            if (filePathUpload == ""):
                message = "Unable to get a response. No keys available."
            else:
                message = "Unable to get a response. No keys available for models that support image uploads."
            
            if (server == "irc.sageru.org"):
                message_prefix = name + ":"
                if (name == "2[Otaku-chan]"):
                    message = chr(0x1D) + "9*Otaku-chan is sleeping. . .*13 7(" + message + ")"
                elif (name == "15[GPT4]"):
                    message = "7" + message
                
            else:
                if (name == "2[Otaku-chan]"):
                    message = chr(0x1D) + "9*Otaku-chan is sleeping. . .*13 7(" + message + ")"
                elif (name == "15[GPT4]"):
                    message = "7" + message
            
            parsed_response = parse_outgoing(message_prefix, message, maxLines, server)
            response_message = parsed_response[0]
            self.setTruncatedPrompt(parsed_response[1])
                
            return response_message
            
        else:   
            with sync_playwright() as playwright_instance:
                if (self.returnDebug() != True):
                    browser = playwright_instance.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
                else:
                    browser = playwright_instance.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
                page = browser.new_page()
                page.goto("http://127.0.0.1:8000/")
                
                page.get_by_title("Character Management", exact=True).click()
                
                if (name == "2[Otaku-chan]"):
                    try:
                        #page.get_by_role("img", name="Otaku-chan").nth(2).click()
                        #page.locator("#rm_print_characters_block").get_by_role("img", name="Otaku-chan", exact=True).click()
                        page.locator("#rm_print_characters_block").get_by_role("img", name="Otaku-chan").first.click()
                    except:
                        #page.get_by_role("img", name="Otaku-chan").first.click()
                        #page.locator("#HotSwapWrapper").get_by_role("img", name="Otaku-chan", exact=True).click()
                        page.locator("#HotSwapWrapper").get_by_role("img", name="Otaku-chan").first.click()
                    page.locator("#avatar_div").get_by_title("Chat Lore").click()
                    page.locator("#dialogue_popup_text").get_by_role("combobox").select_option("Otaku qa Knowledge", timeout=1500)
                    page.get_by_text("Ok", exact=True).click()
                elif (name == "15[GPT4]"):
                    try:
                        page.locator("#rm_print_characters_block").get_by_role("img", name="ChatGPT").click()
                    except:
                        page.locator("#HotSwapWrapper").get_by_role("img", name="ChatGPT").click()
                
                # Command Selection: 
                # regenerate response - Returns message
                # continue response  - Returns message
                # undo 2x messages  - Returns nothing
                # new chat (reset) - Returns nothing
                # system message - Returns nothing
                # normal message  - Returns message
                
                if ((special == "undo") or (special == "reset") or (special == "system")):
                    if (special == "undo"):
                        page.locator("#options_button").click()
                        time.sleep(0.25)
                        page.locator("#option_delete_mes").click()
                        time.sleep(0.25)
                        page.locator('.mes.last_mes').click()
                        time.sleep(0.25)
                        page.locator("#dialogue_del_mes_ok").click()
                        time.sleep(0.25)
                        page.locator("#options_button").click()
                        time.sleep(0.25)
                        page.locator("#option_delete_mes").click()
                        time.sleep(0.25)
                        page.locator('.mes.last_mes').click()
                        time.sleep(0.25)
                        page.locator("#dialogue_del_mes_ok").click()
                        time.sleep(0.25)
                    elif (special == "reset"):
                        self.debug_status = False
                        self.model_status = False
                        self.token_status = False
                        page.locator("#options_button").click()
                        page.locator("#option_start_new_chat").click()
                        page.locator("#dialogue_popup_ok").click()
                    elif (special == "system"):
                        page.get_by_title("API Connections").click()
                        page.locator("#api_button_openai").click(timeout=1500)
                        try:
                            page.get_by_placeholder("Type a message, or /? for help").click(timeout=1000)
                            page.get_by_placeholder("Type a message, or /? for help").fill("/sys " + message) # Input the message
                        except:
                            page.get_by_placeholder("Not connected to API!").click()
                            page.get_by_placeholder("Not connected to API!").fill("/sys " + message) # Input the message
                        with page.expect_response("http://127.0.0.1:8000/api/chats/save", timeout=41500) as response_info:
                            page.get_by_title("Send a message").click()
                else:
                    try:
                        page.get_by_placeholder("Type a message, or /? for help").click(timeout=1000)
                        page.get_by_placeholder("Type a message, or /? for help").fill(message) # Input the message
                    except:
                        page.get_by_placeholder("Not connected to API!").click()
                        page.get_by_placeholder("Not connected to API!").fill(message) # Input the message
                    
                    if (filePathUpload != ""):
                        page.get_by_title("Extras Extensions").click()
                        with page.expect_file_chooser() as fc_info:
                            page.get_by_text("Attach a File").click()
                        file_chooser = fc_info.value
                        file_chooser.set_files(filePathUpload)

                    try:
                        if (openai_gpt4o_skip == True):
                            print(openai_gpt4o_skip_reason)
                            raise ValueError(openai_gpt4o_skip_reason)
                        else:
                            response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "OpenAI", "gpt-4o", "OpenAI-GPT4o", "OpenAI GPT4o", openai_gpt4o_wait_threshold, openai_gpt4o_streaming_response, filePathUpload, special)
                            
                            encountered_error = response_list[0]
                            response_info = response_list[1]
                            temp_response = response_list[2]
                            alternative_message_save = response_list[3]
                            response_message = response_list[4]
                            if (response_list[5] != ""):
                                message_prefix = response_list[5]

                            if (encountered_error == True):
                                raise ValueError()
                    except:
                        if (openai_gpt4o_skip == False):
                            try:
                                page.get_by_title("Abort request").locator("i").click(timeout=100)
                                print("Request aborted due to timeout")
                            except:
                                print("Encountered an error getting a response")
                                time.sleep(5)
                        elif (encountered_error == True):
                            time.sleep(5)
                        else:
                            time.sleep(0)
                        encountered_error = False

                        try:
                            if (openai_gpt4_turbo_skip == True):
                                print(openai_gpt4_turbo_skip_reason)
                                raise ValueError(openai_gpt4_turbo_skip_reason)
                            else:
                                if (filePathUpload == ""):
                                    response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "OpenAI", "gpt-4-turbo", "OpenAI-GPT4-Turbo", "OpenAI GPT4 Turbo", openai_gpt4_turbo_wait_threshold, openai_gpt4_turbo_streaming_response, filePathUpload, special)
                                else:
                                    response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "OpenAI", "gpt-4-vision-preview", "OpenAI-GPT4-Vision", "OpenAI GPT4 Vision", openai_gpt4_turbo_wait_threshold, openai_gpt4_turbo_streaming_response, filePathUpload, special)

                                encountered_error = response_list[0]
                                response_info = response_list[1]
                                temp_response = response_list[2]
                                alternative_message_save = response_list[3]
                                response_message = response_list[4]
                                if (response_list[5] != ""):
                                    message_prefix = response_list[5]

                                if (encountered_error == True):
                                    raise ValueError()
                        except:
                            if (openai_gpt4_turbo_skip == False):
                                try:
                                    page.get_by_title("Abort request").locator("i").click(timeout=100)
                                    print("Request aborted due to timeout")
                                except:
                                    print("Encountered an error getting a response")
                                    time.sleep(5)
                            elif (encountered_error == True):
                                time.sleep(5)
                            else:
                                time.sleep(0)
                            encountered_error = False

                            try:
                                if (azure_gpt4_turbo_skip == True):
                                    print(azure_gpt4_turbo_skip_reason)
                                    raise ValueError(azure_gpt4_turbo_skip_reason)
                                else:
                                    if (filePathUpload == ""):
                                        response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", azure_endpoint_url, proxy_key, message, 8000, name, "Azure", "gpt-4-turbo", "Azure-GPT4-Turbo", "Azure GPT4 Turbo", azure_gpt4_turbo_wait_threshold, azure_gpt4_turbo_streaming_response, filePathUpload, special)
                                    else:
                                        response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", azure_endpoint_url, proxy_key, message, 8000, name, "Azure", "gpt-4-vision-preview", "Azure-GPT4-Vision", "Azure GPT4 Vision", azure_gpt4_turbo_wait_threshold, azure_gpt4_turbo_streaming_response, filePathUpload, special)

                                    encountered_error = response_list[0]
                                    response_info = response_list[1]
                                    temp_response = response_list[2]
                                    alternative_message_save = response_list[3]
                                    response_message = response_list[4]
                                    if (response_list[5] != ""):
                                        message_prefix = response_list[5]

                                    if (encountered_error == True):
                                        raise ValueError()
                            except:
                                if (azure_gpt4_turbo_skip == False):
                                    try:
                                        page.get_by_title("Abort request").locator("i").click(timeout=100)
                                        print("Request aborted due to timeout")
                                    except:
                                        print("Encountered an error getting a response")
                                        time.sleep(5)
                                elif (encountered_error == True):
                                    time.sleep(5)
                                else:
                                    time.sleep(0)
                                encountered_error = False

                                try:
                                    if (openai_gpt4_32k_skip == True):
                                        print(openai_gpt4_32k_skip_reason)
                                        raise ValueError(openai_gpt4_32k_skip_reason)
                                    else:
                                        response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "OpenAI", "gpt-4-32k", "OpenAI-GPT4-32K", "OpenAI GPT4-32K", openai_gpt4_32k_wait_threshold, openai_gpt4_32k_streaming_response, filePathUpload, special)

                                        encountered_error = response_list[0]
                                        response_info = response_list[1]
                                        temp_response = response_list[2]
                                        alternative_message_save = response_list[3]
                                        response_message = response_list[4]
                                        if (response_list[5] != ""):
                                            message_prefix = response_list[5]

                                        if (encountered_error == True):
                                            raise ValueError()
                                except:
                                    if (openai_gpt4_32k_skip == False):
                                        try:
                                            page.get_by_title("Abort request").locator("i").click(timeout=100)
                                            print("Request aborted due to timeout")
                                        except:
                                            print("Encountered an error getting a response")
                                            time.sleep(5)
                                    elif (encountered_error == True):
                                        time.sleep(5)
                                    else:
                                        time.sleep(0)
                                    encountered_error = False
                                
                                    try:
                                        if (azure_gpt4_32k_skip == True):
                                            print(azure_gpt4_32k_skip_reason)
                                            raise ValueError(azure_gpt4_32k_skip_reason)
                                        else:
                                            response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", azure_endpoint_url, proxy_key, message, 8000, name, "Azure", "gpt-4-32k", "Azure-GPT4-32K", "Azure GPT4-32K", azure_gpt4_32k_wait_threshold, azure_gpt4_32k_streaming_response, filePathUpload, special)

                                            encountered_error = response_list[0]
                                            response_info = response_list[1]
                                            temp_response = response_list[2]
                                            alternative_message_save = response_list[3]
                                            response_message = response_list[4]
                                            if (response_list[5] != ""):
                                                message_prefix = response_list[5]

                                            if (encountered_error == True):
                                                raise ValueError()
                                    except:
                                        if (azure_gpt4_32k_skip == False):
                                            try:
                                                page.get_by_title("Abort request").locator("i").click(timeout=100)
                                                print("Request aborted due to timeout")
                                            except:
                                                print("Encountered an error getting a response")
                                                time.sleep(5)
                                        elif (encountered_error == True):
                                            time.sleep(5)
                                        else:
                                            time.sleep(0)
                                        encountered_error = False
                                    
                                        try:
                                            if (aws_claude_sonnet_skip == True):
                                                print(aws_claude_sonnet_skip_reason)
                                                raise ValueError(aws_claude_sonnet_skip_reason)
                                            else:
                                                response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "claude", aws_endpoint_url, proxy_key, message, 8000, name, "AWS", "claude-3-sonnet-20240229", "Claude-3-Sonnet", "AWS Claude Sonnet", aws_claude_sonnet_wait_threshold, aws_claude_sonnet_streaming_response, filePathUpload, special)

                                                encountered_error = response_list[0]
                                                response_info = response_list[1]
                                                temp_response = response_list[2]
                                                alternative_message_save = response_list[3]
                                                response_message = response_list[4]
                                                if (response_list[5] != ""):
                                                    message_prefix = response_list[5]

                                                if (encountered_error == True):
                                                    raise ValueError()
                                        except:
                                            if (aws_claude_sonnet_skip == False):
                                                try:
                                                    page.get_by_title("Abort request").locator("i").click(timeout=100)
                                                    print("Request aborted due to timeout")
                                                except:
                                                    print("Encountered an error getting a response")
                                                    time.sleep(5)
                                            elif (encountered_error == True):
                                                time.sleep(5)
                                            else:
                                                time.sleep(0)
                                            encountered_error = False
                                        
                                            try:
                                                if (aws_claude_skip == True):
                                                    print(aws_claude_skip_reason)
                                                    raise ValueError(aws_claude_skip_reason)
                                                else:
                                                    response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", aws_endpoint_url, proxy_key, message, 8000, name, "AWS", "anthropic.claude-v2:1", "Claude-2.1", "AWS Claude 2.1", aws_claude_wait_threshold, aws_claude_streaming_response, filePathUpload, special)

                                                    encountered_error = response_list[0]
                                                    response_info = response_list[1]
                                                    temp_response = response_list[2]
                                                    alternative_message_save = response_list[3]
                                                    response_message = response_list[4]
                                                    if (response_list[5] != ""):
                                                        message_prefix = response_list[5]

                                                    if (encountered_error == True):
                                                        raise ValueError()
                                            except:
                                                if (aws_claude_skip == False):
                                                    try:
                                                        page.get_by_title("Abort request").locator("i").click(timeout=100)
                                                        print("Request aborted due to timeout")
                                                    except:
                                                        print("Encountered an error getting a response")
                                                        time.sleep(5)
                                                elif (encountered_error == True):
                                                    time.sleep(5)
                                                else:
                                                    time.sleep(0)
                                                encountered_error = False
                                        
                                                try:
                                                    if (openai_gpt3_5_turbo_skip == True):
                                                        print(openai_gpt3_5_turbo_skip_reason)
                                                        raise ValueError(openai_gpt3_5_turbo_skip_reason)
                                                    else:
                                                        response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "OpenAI", "gpt-3.5-turbo-16k", "GPT-3.5-Turbo-16K", "OpenAI GPT-3.5-Turbo-16K", openai_gpt3_5_turbo_wait_threshold, openai_gpt3_5_turbo_streaming_response, filePathUpload, special)

                                                        encountered_error = response_list[0]
                                                        response_info = response_list[1]
                                                        temp_response = response_list[2]
                                                        alternative_message_save = response_list[3]
                                                        response_message = response_list[4]
                                                        if (response_list[5] != ""):
                                                            message_prefix = response_list[5]

                                                        if (encountered_error == True):
                                                            raise ValueError()
                                                except:
                                                    if (openai_gpt3_5_turbo_skip == False):
                                                        try:
                                                            page.get_by_title("Abort request").locator("i").click(timeout=100)
                                                            print("Request aborted due to timeout")
                                                        except:
                                                            print("Encountered an error getting a response")
                                                            time.sleep(5)
                                                    elif (encountered_error == True):
                                                        time.sleep(5)
                                                    else:
                                                        time.sleep(0)
                                                    encountered_error = False
                                        
                                                    try:
                                                        if (google_gemini_skip == True):
                                                            print(google_gemini_skip_reason)
                                                            raise ValueError(google_gemini_skip_reason)
                                                        else:
                                                            response_list = self.proxyPrompt(sendmsg, sourceChannel, browser, page, "custom", openai_endpoint_url, proxy_key, message, 8000, name, "Google", "gemini-pro", "Gemini-Pro", "Google Gemini Pro", google_gemini_wait_threshold, google_gemini_streaming_response, filePathUpload, special)

                                                            encountered_error = response_list[0]
                                                            response_info = response_list[1]
                                                            temp_response = response_list[2]
                                                            alternative_message_save = response_list[3]
                                                            response_message = response_list[4]
                                                            if (response_list[5] != ""):
                                                                message_prefix = response_list[5]

                                                            if (encountered_error == True):
                                                                raise ValueError()
                                                    except:
                                                        pass

                        
                
                page.get_by_title("AI Response Configuration").click()
                maxTokensContext = int(page.locator("#openai_max_context_counter").input_value()) # Get the maxTokensContext
                
                time.sleep(3) # Wait for SillyTavern to save the response. If this is not done, although a message may be generated, it won't be saved. 
                
                if ((special != "undo") and (special != "reset") and (special != "system") and (alternative_message_save == False)):
                    original_response = response_info.value
                    original_response = str(original_response.json()) #json.dumps(response.json())
                browser.close()
            if ((special != "undo") and (special != "reset") and (special != "system") and (alternative_message_save == False)):
                if (self.returnDebug() == True):
                    print("\nJSON:\n" + original_response + "\n\n")
                
                temp_response = original_response
                
                # Check if the input is a list (indicating it has been split)
                if isinstance(original_response, list):
                    # Join the list elements into a single string using the join method
                    temp_response = ''.join(original_response)
                
                tokenUtilization = ""
                if (self.returnTokens() == True):
                    try:
                        if (self.returnDebug() == True):
                            print("TEMP RESPONSE:\n" + temp_response)
                        #OpenAI Token Counts
                        tokenCounts = temp_response.split("'usage': ")[1].split("}, ")[0] + "}"
                        data_dict = eval(tokenCounts)
                        #tokenResponseUsage = data_dict['completion_tokens']
                        promptTokenUsage = data_dict['total_tokens']
                    except:
                        promptTokenUsage = 4096
                        
                    padding = int(len(str(maxTokensContext)) - len(str(promptTokenUsage)))

                    zeroPadding = ""
                    for x in range(padding):
                      zeroPadding += "0"
                    
                    if (self.returnDebug() == True):
                        tokenUtilization = "[" + zeroPadding + str(promptTokenUsage) + "/" + str(maxTokensContext) + "]"
                    else:
                        tokenUtilization = "[" + str(promptTokenUsage) + "]"
                    
                    if(int(promptTokenUsage) <= (maxTokensContext / 4)):
                        tokenUtilization = "3" + tokenUtilization
                    elif(int(promptTokenUsage) <= (maxTokensContext / 2)):
                        tokenUtilization = "8" + tokenUtilization
                    elif(int(promptTokenUsage) <= (maxTokensContext * 3 / 4)):
                        tokenUtilization = "7" + tokenUtilization
                    else:
                        tokenUtilization = "4" + tokenUtilization
                
                if (server == "irc.sageru.org"):
                    message_prefix = name + message_prefix
                    
                    if (self.returnTokens() == True):
                        message_prefix += "|" + tokenUtilization + ":"
                    else:
                        message_prefix +=  ":"
                elif (self.returnTokens() == True):
                    message_prefix += tokenUtilization + ":"
                    
                try:
                    try:
                        data_dict = eval(temp_response)
                        message = data_dict['choices'][0]['message']['content']
                    except:
                        try:
                            message = temp_response.split("'content': '")[1].split("'}, 'logprobs'")[0]
                        except:
                            message = temp_response.split("'content': \"")[1].split("\"}, 'logprobs'")[0]
                    if (self.returnDebug() == True):
                        print("\n\nMESSAGE:\n" + message + "\n\n")
                    
                    if (message.find('Proxy error') != -1):
                        message = "7Unable to get a response."
                    
                    parsed_response = parse_outgoing(message_prefix, message, maxLines, server)
                    response_message = parsed_response[0]
                    self.setTruncatedPrompt(parsed_response[1])

                except:
                    try:
                        data_dict = eval(temp_response)
                        message = str(data_dict['error']['message'])
                    except:
                        message = "We couldn't get a response for you, please try again"
                    
                    parsed_response = parse_outgoing(message_prefix, message, maxLines, server)
                    response_message = parsed_response[0]
                    self.setTruncatedPrompt(parsed_response[1])
                    
            elif (alternative_message_save == True):
                if (server == "irc.sageru.org"):
                    message_prefix = name + message_prefix + ":"
                
                parsed_response = parse_outgoing(message_prefix, message, maxLines, server)
                response_message = parsed_response[0]
                self.setTruncatedPrompt(parsed_response[1])
                
            return response_message