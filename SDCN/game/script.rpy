init python:
    import os, subprocess, json, re
    from datetime import datetime
    prompt = ""
    newbg = "newbg"
    quitwait = 0
    quittime = 100
    runmode = "/k" #set to "/c" for cmd windows to disappear when done; "/k" makes it stay open for debugging

define e = Character("Guide guy")

label start:
    scene black
    show disembodied guide guy
    e "Here is a simple renpy script that calls stable diffusion to create custom CGs live."
    e "Since it is similar, will show you also how to make regular custom BGs live."
    e "But before we start, make sure your Stable Diffusion webui is on with the '--api' flag in webui-user.bat with 'set COMMANDLINE_ARGS= --api'."
    #e "Can also add '--listen' to use SD across devices connected by the same network"
    e "Make sure you've also installed 'webuiapi' with pip."
    e "Ok. I will now open the Stable Diffusion python script here now."
    #Run the Stable Diffusion python script before game starts
    $ subprocess.Popen(["start", "cmd", runmode, "python " + config.basedir + "/game/sdpyscript.py"], shell=True)
    e "I hope that worked..."
    e "Now, turn on developer mode by pressing 'd'."
    e "The script should reload if you're not already in developer mode. With this, the new backgrounds and CGs should be able to be loaded in on the go after generation."
    e "With all that set, here's the simple script for SD in renpy- the janky way we did it, anyway."
    e "Hope this is working so far..."
    while prompt != "exit":
        $ prompt = renpy.input("> Type 'exit' to quit, '<GO TO location prompt>' to change BG, or '<GO TO location prompt (CG)>' for CG: ")
        if "<GO TO " in prompt and ">" in prompt:
            python:
                sdprompt = prompt.split("<GO TO ")[1].split(">")[0]
                if "(cg)" in prompt.lower():
                    renpy.say(e, "Changing background to CG!")
                    cg = True
                else:
                    renpy.say(e, "Changing background!")
                    cg = False
                renpy.scene()
                renpy.show("black")
                renpy.with_statement(dissolve)

                #clearing away temp files from previous generations, if any
                try: os.remove(config.basedir + "/game/done.txt")
                except: pass

                #MOVE OLD BG AWAY! (only if you want to save your previously generated BGs/CGs. Else you can straight up delete them with something like os.remove(config.basedir + "/game/images/newbg.png"))
                try: os.rename(config.basedir + "/game/images/newbg.png", config.basedir + datetime.now().strftime("/game/images/%m'%d'%Y-%H'%M'%S_newbg.png")) #FIX
                except: pass

                #then write the prompt to prompts.txt file, so python script can see it!
                with open(config.basedir + "/game/prompts.txt", 'w') as f:
                    f.write(sdprompt)

                #wait until the bg/cg is generated
                while not os.path.isfile(config.basedir + "/game/done.txt"):
                    renpy.say(e, "{w=0.5}.{w=0.5}.{w=0.5}.{w=0.5}{nw}")
                    quitwait += 1
                    if quitwait > quittime:
                        renpy.say(e, "Timing out...")
                        renpy.quit()
                quitwait = 0
                renpy.pause(1)
                renpy.scene()
                renpy.show(newbg)
                renpy.with_statement(dissolve)
                if cg:
                    renpy.say("", "...")
                else:
                    renpy.show("disembodied guide guy")
                    renpy.with_statement(dissolve)

                result = prompt.split("<GO TO ")[0] + "*We go to " + sdprompt + "* " + prompt.split(">")[1]
                renpy.say(e, result.replace("(cg)", "").replace("(CG)", ""))

    #exit flag here
    python:
        with open(config.basedir + "/game/exit.txt", 'w') as f:
            pass
    e "And that's how we did it."
    e "Hopefully that worked for you. Unfortunately as of this script, this only works in renpy developer mode which you will need to manually activate every time..."
    e "Still can use lots more improvement. For one, you don't have to use such tags with angled brackets since they could stick out like sore thumbs in story dialogue."
    e "Feel free to change them- to improve on the code."
    e "With that, goodbye now."
    return
