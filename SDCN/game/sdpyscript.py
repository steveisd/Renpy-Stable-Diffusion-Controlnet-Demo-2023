"""
Edit as needed, may not work as is!
"""
#When run, the two lines below should hide this window (comment away if needed)
import ctypes
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)

#IMPORT - make sure you have 'webuiapi' from https://github.com/mix1009/sdwebuiapi installed
import json, os, requests, random, webuiapi
from time import sleep
from datetime import datetime
from PIL import Image

#DEFINE VARS AND FUNCS
prepend = "/".join(os.path.abspath(__file__).split("\\")[:-1])
bg = True
prompt = ""
counter = 0

bg_model = "revAnimated_v122.safetensors" #put your background SD model here, i.e. "background.ckpt" or "background.safetensors"
char_model = "sa1-1800.ckpt" #put your character's SD model here; if none, you can set to bg_model and instead use lora/set of prompts- see below for this with "keyword" var

#positive and negative prompts for your bg_model
pos_prompt = "masterpiece, best resolution, detailed shading, vibrant colors, (background), ((no people))"
neg_prompt = "people, multiple people, ugly, lowres, text, error, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name"
#and then for your char_model- might want to adjust as needed to deal with duplicate people
char_pos_prompt = "((solo)), highres, best quality, best resolution, detailed skin"
char_neg_prompt = "cropped, ugly, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name"

address = "127.0.0.1" #your ip address, edit as needed
port = 7860 #your port, edit as needed: SD webui uses 7860 as default
api = webuiapi.WebUIApi(host=address, port=port)
options = {}
options["sd_model_checkpoint"] = bg_model #loads bg_model as default when starting
api.set_options(options)

#remove old temp files, if any
try: os.remove(prepend + "/exit.txt")
except: pass
try: os.remove(prepend + "/prompts.txt")
except: pass

#LOOP, this script runs in the background until exiting renpy
while True:
    #while not called with a temp prompts.txt file, just run idly in bg
	while not os.path.isfile(prepend + "/prompts.txt"):
		print("Waiting...")
		sleep(1)
		if os.path.isfile(prepend + "/exit.txt"):
			exit()

    #When prompts detected, opens, reads, and feeds its prompt content to SD API
	with open(prepend + "/prompts.txt", "r") as f:
		prompt = f.read()

	#remove temp prompts file when done to avoid breaking communication between scripts
	try: os.remove(prepend + "/prompts.txt")
	except: pass

	#check if CG or BG to switch models here and then generate as needed
	if "(cg)" in prompt.lower():
		options["sd_model_checkpoint"] = char_model
		bg = False
	else:
		options["sd_model_checkpoint"] = bg_model
		bg = True
	api.set_options(options)

	if bg: #as usual, edit as needed and check the webuiapi documentation https://github.com/mix1009/sdwebuiapi for more details
		r1 = api.txt2img(prompt=pos_prompt + ", " + prompt,
					negative_prompt=neg_prompt,
					width=1280, #change to match
					height=720, #your renpy resolution
                    steps=24,
					cfg_scale=10,
					)
		r1.image.save(prepend + '/images/newbg.png')

	else:
        #this line looks into the folder of poses and picks a random one to generate character on
		img = Image.open(prepend + "/poses/" + random.choice(os.listdir(prepend + "/poses")))

		#BONUS VARS HERE! With your renpy project, you can have all sorts of variables from story/chat that you can also feed into here as prompts to enhance the generated pictures to tie into them better. Some examples are:
		expression = "neutral" #we used sentiment analysis to pull out these expressions
		appearance = "pink hair, short hair, blue eyes"
		current_wear = "pink shirt, blue shorts"
		doing = "smiling"
        #Note: you can ignore these if it confuses you and focus on just CGs and BGs. Just remove the corresponding variables or edit as needed. Again, feel free to improve them too if you plan to use them anyway

		keyword = "sayori" #this is where you put your char's name/other trigger word or your lora for your character, like "sayori \(doki doki literature club\)" or "<lora:sayori:1>"

		#Then generate CG. Again, adjust as needed!
		unit1 = webuiapi.ControlNetUnit(input_image=img, module='openpose', model='control_v11p_sd15_openpose.safetensors', weight = 1, guidance = 1) #If you get lost for the preprocessor and models: valid module values can be found at dropdown menu of controlnet extension. As for models, check out https://github.com/mix1009/sdwebuiapi#extension-support---controlnet on how you can list your available models
		r2 = api.txt2img(prompt=keyword + ", " + char_pos_prompt + ", " + expression + ", " + appearance + ", " + current_wear + ", " + doing + ", " + prompt,
					negative_prompt=char_neg_prompt,
					denoising_strength=0.7,
					sampler_index="Euler a",
					enable_hr=True,
					hr_scale=1,
					width=1280,
					height=720,
					cfg_scale=7.5,
					controlnet_units=[unit1]
					)
		r2.image.save(prepend + '/images/newbg.png')

	with open(prepend + "/done.txt", "w") as f: pass
	#and loop till done
