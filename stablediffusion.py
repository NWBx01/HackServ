from utilities import * # import the utilities.py file.

########### Stable Diffusion Stuff Here ###############
#######################################################

class StableDiffusion:    
    def prompt(self, message):
        url = "http://127.0.0.1:7860/run/predict/"

        payload = {
          "data":[
            "task(wnz5u0j0gtknzwv)",
            message,
            "(worst quality, low quality:1.4), realistic, nose, 3d, greyscale, monochrome, text, title, logo, signature",
            [],
            30,
            "DPM++ 2S a",
            1,
            1,
            10,
            768,
            576,
            True,
            0.5,
            1.5,
            "4x-UltraSharp",
            15,
            0,
            0,
            "Use same checkpoint",
            "Use same sampler",
            "",
            "",
            [],
            "None",
            False,
            "",
            0.8,
            -1,
            False,
            -1,
            0,
            0,
            0,
            0,
            False,
            False,
            "positive",
            "comma",
            0,
            False,
            False,
            "start",
            "",
            "Seed",
            "",
            [],
            "Nothing",
            "",
            [],
            "Nothing",
            "",
            [],
            True,
            False,
            False,
            False,
            False,
            False,
            False,
            0,
            False,
            [],
            "",
            "",
            ""
            ],
          "event_data": None,
          "fn_index":102,
          "session_hash":"3yylwwkyuaw"
        }

        payload = json.dumps(payload)

        headers = {
            "User-Agent": useragent,
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "http://127.0.0.1:7860/",
            "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:7860",
            "DNT": "1",
            "Connection": "keep-alive",
            "Cookie": "serv={}",
            "Sec-GPC": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        
        query = requests.post(url=url, headers=headers, data=payload)
        response = query.text

        
        #print(response)
        
        try:
            
            try:
                firstPart = response.split(("\"data\":[[{\"name\":\""))[1]
                secondPart = firstPart.split(("\",\"data\""))[0]
                filepath = secondPart.split((".png?"))[0] + ".png"
                
                #print("Filepath: " + filepath)
                
                # Can use either catbox (litterbox) or x0.at, and likely many, many more
                try:
                    url = litterboxUpload(filepath)
                except:  
                    url = x0atUpload(filepath)
                
                messages = ["" + url]
            except:
                messages = ["7Error"]
            
        except IndexError:
            # raise IndexError()
            
            data = json.loads(response)
            message = str(data["detail"])
            #print(message)
            
            #return ["7We couldn't get a response for you, please try again"]
            
            messages = ["7" + message]
            
        return messages