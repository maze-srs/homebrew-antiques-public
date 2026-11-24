init python:
    #ART LOADER: use drawings in game/images; fallback: ren'py placeholder
    def art(filename, fallback):
        path="images/" + filename
        if renpy.loadable(path):
            return path
        return fallback

    #the fallback:
    def sprite(filename, base="girl", tint="#cccccc", zoom=1.0):
        return art(filename, Transform(Placeholder(base), matrixcolor=TintMatrix(tint), zoom=zoom))

    #AUDIO FINDER: audio in game/audio/<name>; fallback 0.1s of silence
    def find_audio(name):
        for ext in (".ogg", ".mp3", ".wav", ".opus", ".flac"): # possible extentions
            path="audio/" + name + ext
            if renpy.loadable(path):
                return path
        return "<silence 0.1>"

    SPOTLIGHT_IGNORE={"bg"}

    #Speaker Factory
    def Speaker(name, tag=None, **kwargs):
        return Character(name, image=tag, callback=spotlight_callback(tag), **kwargs)
    
    #Spotlight speaker function
    def spotlight_callback(tag):
        def callback(event, interact=True, **kwargs):
            if event!="begin":
                return

            #every "character" on screen
            tag_list= [t for t in renpy.get_showing_tags("master") if t not in SPOTLIGHT_IGNORE]
            #if the speaker isn't on screen, nobody gets dimmed
            speaker=tag if tag in tag_list else None
            
            for t in tag_list:
                shouldFocus= (speaker is None) or (t == speaker)
                #collect transforms, only swap dim/bright
                transforms = []
                for x in (renpy.get_at_list(t) or []):
                    if x not in (sprite_dim, sprite_bright):
                        transforms.append(x)
                renpy.show(t, at_list= transforms + [sprite_bright if shouldFocus else sprite_dim])
        return callback
# END INIT
#+++++++++++++++

# Non-speaker colour and transforms
define dim_color=SaturationMatrix(0.0) * BrightnessMatrix(-0.25)
transform sprite_dim:
    matrixcolor dim_color
transform sprite_bright:
    matrixcolor IdentityMatrix()

#CHARACTERS:
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
define pc       =Speaker("You", "pc", color="#ffd9a0")
define thought  =Speaker("You", "pc", color="#ffd9a0", what_color="#aab0bb")
define witch    =Speaker("[witch_name]", "witch", color="#c58cff")
define masked   =Speaker("Masked Guy", "masked", color="#9ad0ff")
define soldier  =Speaker("Soldier", "soldier", color="#c9b07a")
define child    =Speaker("Child", "child", color="#f0a0c0")
define narrator =Speaker(None)

image bg shop       =art("bg shop.png",       Solid("#4a3526"))
image bg shopcursed =art("bg shopcursed.png", Solid("#3d5a2b"))   
image bg shopnight  =art("bg shopnight.png",  Solid("#0b0b1a"))   
image pc human      =sprite("human.png",  "boy", "#d9c8b4")
image pc goblin     =sprite("goblin.png", "boy", "#8be06a")
image witch neutral =sprite("witch_neutral.png", "girl", "#b58cff")
image witch smirk   =sprite("witch_smirk.png",   "girl", "#e8c4ff")   
image witch angry   =sprite("witch_angry.png",   "girl", "#ff5a8a")
image masked masked =sprite("masked.png", "boy", "#c8c8d0")
image masked fidget:
    "masked masked"
    xoffset 0 yoffset 0
    ease 0.12 xoffset -8
    ease 0.12 xoffset 8
    ease 0.12 xoffset -4 yoffset -6
    ease 0.12 xoffset 0 yoffset 0
    pause 0.5
    repeat
image soldier       =sprite("soldier.png", "boy", "#a8b890")
image child         =sprite("child.png", "girl", "#ffc8dc")

#AUDIO FILES:
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#game/audio/SFX 
define sfx_bell  =find_audio("SFX/StoreBell")          # a customer walks in
define sfx_boom  =find_audio("SFX/VineBoom")           # the clerk turns into a goblin
define sfx_cash  =find_audio("SFX/CashRegister")       # money changes hands
#game/audio/Soundtrack
define music_store  =find_audio("Soundtrack/NormalStore")   # normal shop
define music_witch  =find_audio("Soundtrack/AngryWitch")    # the witch loses it
define music_goblin =find_audio("Soundtrack/GoblinMode")    # when making a choice as a goblin

#SCRIPTING SHIT:
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#Constants
define AMULET_VALUE=100
define ENDING_HUMAN_MAX=1 #this or lower: you stayed human
define ENDING_GOBLIN_MIN=3 #this or higher: happy goblin

#Variables
default witch_name="???"
default goblin_level=0 #0 to 5
default offer=0 

define curse_flash=Fade(0.1, 0.0, 0.8, color="#7dff6a")

#Goblin instinct meter
screen goblin_hud():
    zorder 100
    frame:
        align (0.99, 0.01)
        padding (14, 8)
        vbox:
            spacing 6
            text "Goblin instinct"
            bar value StaticValue(goblin_level, 5) xysize (220, 18)

#Items in inventory: (name, value in gold, colour)
define shop_items=[
    ("Brass Cuckoo Clock",  120, "#8a6a2a"),
    ("Chipped Teacup",      5, "#8a8f9a"),
    ("Rocking Horse",       40, "#7a4a3a"),
    ("Silver Spoon",        15, "#6a7a8a"),
    ("Dusty Globe",         60, "#3a6a8a"),
    ("Cracked Mirror",      25, "#5a5a7a"),
    ("Stuffed Owl",         85, "#6a5a3a"),
    ("Old Telephone",       30, "#3a3a3a"),
    ("Plain White Mask",    30, "#d8d8d8"),
]

#Shop inventory: heavily commented for whoever wants to learn<3
screen inventory_screen(can_go_back=True):
    modal True #cannot interact with the game behind 
    add Solid("#000000aa") #black semitransparent layer over the game
    $ tip=GetTooltip() #for the mouse-over, works with tooltip property of the item icons

    frame: #the actual inventory
        align (0.5, 0.5) #inventory is in the middle of the screen (0,0 is in the top left corner)
        xsize 600 #fixed width (otherwise fills the screen) (i pulled 600 out of my ass, I just needed a big enought box)
        padding (0, 25) #0px for left and right and 25px for top and bottom (otherwhise the title was too flush with the top of the inventory frame)

        vbox: #invisible container that stacks its children from top to bottom
            xfill True #takes the size of the container (in this case the frame)
            spacing 18 #18px between each stacked item (another random number, I just wanted it slightly bigger than the space between objecs in the inventory)
            #Inside this container there are 4 children:

            #1)The title
            text "Inventory" size 40 xalign 0.5

            #2)The grid
            vpgrid: #grid that fills row by row
                cols 4 #4 colums 
                spacing 12 #12px between cells
                xysize (476, 354) #grid's width and height. What are these magic numbers? \/ (each button id 110*110)
                #4 buttons of 110 plus 3 gaps of 12 make 476, and 3 rows of 110 plus 2 gaps make 354.
                allow_underfull True #allow the last row to be partially empty -> otherwise ren'py whines
                xalign 0.5 #horizontaly centered in the vbox
                for item in shop_items: #shop_items is a list defined before the definition of the inventory
                    button: #each item inventory is shown as a button
                        xysize (110, 110) #random width and hight that I felt beeing ok
                        background Solid(item[2]) #takes the color form the list
                        hover_background Solid("#f2e3b0") #hover_background is a style property
                        text item[0][0] size 48 color "#ffffff" hover_color "#4a3526" align (0.5, 0.5) #what is shown (first letter of the item)
                        tooltip item #the tooltip is a property of a button and works with GetTooltip(), defined at the beginning of the "screen section" (we are saving all the info of "item" inside the button, under the name "tip")
                        action Return(item[0]) #the action is a property of a button and detect the left click. Used to return the name of the item if the button is pressed
                        
            #3)The information box of the item
            frame:
                xsize 476 #same width as the grid
                ysize 90 #random hight
                xalign 0.5 #centered
                if tip: #the info we got from each button with "$ tip=GetTooltip()" and "tooltip item" is not None
                    vbox:
                        align (0.5, 0.5)
                        text "[tip[0]]" size 30 xalign 0.5 #first child of the vbox (you use "tip" just like you used "item" before)
                        text "Value: [tip[1]] gold" size 24 xalign 0.5 #second child of the vbox
                else:
                    text "Hover over an item to inspect it" size 24 color "#aaaaaa" align (0.5, 0.5)

            #4)The back button
            if can_go_back:
                textbutton "Back" action Return("back") xalign 0.5

#SCENES
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
label start:
    $ witch_name="???"
    $ goblin_level=0

    scene bg shop with fade
    play music music_store fadein 1.0
    show pc human at left with dissolve
    play sound sfx_bell

    pc "Welcome to Homebrew Antiques. What can I help you wi-?"

    show witch neutral at right with moveinright

    witch "Doest thou possess this jewel? 'Tis blue and purple, and infused with the magic of the Old World?"

    pc "Like. A sapphire?"

    show witch angry
    witch "No! 'Tis purple! And blue! And infused with magic!"

    pc "So, like a crystal?"

    show witch neutral
    witch "Oh, my God, yes, a crystal then. Do you possess it?"

    pc "I can look for one in the back?"

    witch "Then do so! Thou art wasting my time!"

    call crystal_search
    play music music_witch fadeout 0.5 fadein 0.5

    show witch angry
    witch "Ah, curses! Does't thou not have any crystals at hand??"

    pc "We can order some-"

    witch "Then do that for Guggol's sake!"

    pc "... but that'd take 3-5 business days to deliver."

    witch "Excuse you?! Thou treat them as stock?!"

    witch "Where is your manager?! This behaviour is unacceptable!"

    pc "I'm sorry to inform you lady, but you're speaking to the manager."

    witch "..."

    with hpunch
    witch "Curses!"
    witch "Thou art naught but some simpleton!"
    witch "Thou wilt regret thine transgressions!"
    witch "Prepare thyself!"

    pc "Uh, okay, sure..."

    jump shop_morning

label crystal_search:
    menu:
        "Open inventory":
            call screen inventory_screen
            if _return!="back":
                show witch angry
                witch "You idiot, this is not what I wanted!"
            jump crystal_search

        "\"Sorry lady, no purple crystals in stock right now.\"":
            pc "Sorry lady, no purple crystals in stock right now."
            return


label shop_morning:
    scene bg shop with fade
    show pc human at left with dissolve
    play music music_store fadeout 1.0 fadein 1.0

    thought "Man. I hate this job."
    thought "It's the same thing every day. Wake up, brush teeth, open shop."
    thought "Customers are sparse. No one wants this old stuff anymore."
    thought "Actually, how long have we been open? Let me check."
    thought "8:24? What do you mean it's only been 20 minutes?!"
    thought "Wait, hold on."

    play sound sfx_boom
    show pc goblin
    with hpunch

    thought "What the hell?"
    thought "...You've got to be kidding me."
    thought "What are these even? Sharp teeth? Goblin ears?"
    thought "...Really? Again?"
    thought "Because of one jewel I literally didn't have?"
    thought "Ugh, whatever. I'll make a doctor's appointment."
    thought "..."
    thought "What a Karen."

    play sound sfx_bell
    show masked masked at right with moveinright
    pause 1.0
    jump masked_guy

label masked_guy:

    pc "Welcome, how can I help you? Please ignore the ears and teeth. It's been a long week."

    masked "Uh, sure?"

    show masked fidget
    masked "So, uhm, I'm looking for... something."

    pc "Right. That is?"

    masked "Uhm, you know about, like, items that have certain, uh, influences?"

    pc "Like. On people? Or the environment?"

    show masked masked
    masked "People! Definitely people!"

    pc "Uh, sure. And what item exactly?"

    masked "So, you know. Something that one may or may not be able to, uh, hang on their being?"

    pc "I'm sorry?"

    masked "Oh, don't be! It's a difficult request."

    thought "Bruh."

    menu:
        "Tell them to get to the point.":
            pc "Just tell me what you want, man. I don't get paid enough for this."
            masked "I thought you're the manager?"
            pc "Don't question it."

        "Be a good customer service employee.":
            pc "Look. If you tell me exactly what you want, I can be of more help."

        "Just walk away.":
            pc "You know what? I give up."
            masked "H-huh?!"
            pc "Nope. Not doing it."
            masked "W-wait! Please! I'll be more specific."
            thought "This better be worth it."

    masked "O-okay. Well, uhm, it's like something like this."

    thought "Did they just... Gesture, with their hands, their face"
    thought "Wait."

    pc "...So you want another mask?"

    masked "N-no... But do you happen to have one?"

    thought "Bruh times two."

    pc "Yeah, I have one in the back. Let me grab it real quick."

    jump mask_search

label mask_search:
    call screen inventory_screen(can_go_back=False)
    if _return!="Plain White Mask":
        masked "Mh... this is not what I'm searching for..."
        jump mask_search

    pc "Here you go. That'll be-"

    thought "Huh. My hands feel so... heavy? Like lead."
    thought "What's going on? Why do I suddenly feel so... sad?"

    show masked fidget
    masked "Y-yes? How much?"

    show screen goblin_hud with dissolve
    thought "Gold."
    thought "Shiny. And sparkly."
    thought "And worth so much more than this lame mask."
    thought "Right?"

    play music music_goblin fadeout 0.5 fadein 0.5
    menu:
        "Say the correct amount.":
            pc "That would be 30 gold pieces."
            masked "Oh goodness gracious, at least the prices have remained somewhat fair."

        "Demand more gold.":
            $ goblin_level+=1                      
            $ renpy.notify("Goblin instinct +1")
            pc "Actually, uhm, that'll be... 50? Gold?"
            masked "Is that a question?"
            pc "No?"
            masked "O-okay. Here you go."
    play music music_store fadeout 1.0 fadein 1.0

    play sound sfx_cash
    thought "Gold! Heck yeah!"

    pc "Please, do come back!"

    jump soldier_scene

label soldier_scene:
    scene black with fade
    pause 1.0
    scene bg shop
    show pc goblin at left
    with fade
    play sound sfx_bell

    show soldier at right with moveinright
    soldier "Hey you... uh... do you like, purchase stuff from your customers as well?"

    pc "We sure did in the past. Let me see what you have."

    soldier "So there's this amulet of mine. Don't really know how, but it protects me from magic. You know, fireballs and stuff... The war..."

    soldier "Survived a lightning strike by this bearded guy once and pushed the nerd off his tower!"

    pc "Right. An amulet to push wizards with."

    soldier "Mainly to protect me from wizards. Times have been rough and uuuh... I kinda need to eat."

    soldier "But you know how it is. Different country, different currency."

    thought "Nope, I really don't."

    soldier "How much is it worth?"

    thought "Let's see... It's worth about [AMULET_VALUE] gold."

    play music music_goblin fadeout 0.5 fadein 0.5
    jump soldier_price

label soldier_price:
    $ offer=renpy.input("How much gold do you offer him?", allow="0123456789", length=5).strip()
    if offer=="" or offer==0:
        $ renpy.notify("Please type an amount.")
        $ offer=0
        jump soldier_price

    $ offer=int(offer)
    pc "How about [offer] gold?"

    if offer<AMULET_VALUE:
        $ goblin_level=min(5, goblin_level + 1)
        $ renpy.notify("Goblin instinct +1")
    elif offer>AMULET_VALUE:
        $ goblin_level=max(0, goblin_level - 1)
        $ renpy.notify("You are fighting your goblin nature!")

    play music music_store fadeout 1.0 fadein 1.0
    play sound sfx_cash
    soldier "Thank you so much!"

    soldier "I'll make sure to feed my grandchildren with this!"

    jump child_scene

label child_scene:

    scene black with fade
    pause 1.0
    scene bg shop
    show pc goblin at left
    with fade
    play sound sfx_bell
    show child at right with moveinright

    pc "Welcome, how can I hel-?"

    child "Mister. I require your help. It's urgent. I need a rock crystal, clear as the first spring's dew."

    pc "Right. What kind?"

    child "One from the local mountains would do just fine. I should be able to read the letters of a book by looking through it."

    pc "Clear quartz crystals we have plenty. Most of them are from the Train Tip, right up north. Been there lately?"

    child "No time for chatter, Miss. I urge you to hurry and fetch that crystal for me."

    pc "Relax, little guy. Uh, I mean, little girl?"

    pc "I'll be right back."

    pc "Wait, how urgent you said this was?"

    child "Just know, many more fates than just mine are tied to the timely delivery of this crystal. Is that clear enough for you?"

    pc "Riiiight. The utmost urgent crystal, from the utmost highest spot of the Train Tip. Clear as dew, might as well be a reading glass. Coming right up. That'll be..."

    play music music_goblin fadeout 0.5 fadein 0.5
    menu:
        "Give it to her for free.":
            $ goblin_level=max(0, goblin_level-1)
            $ renpy.notify("You are fighting your goblin nature!")

            child "Wait... don't you demand anything in return? Not even a payment?"

            pc "Take it. It's yours. I can tell you need it more than just desperately."

            child "That's it... I have assembled everything! My village might be saved after all."

            pc "Your village you say?"

            child "A terrible plague has befallen my village. It has killed dozens and threatens the lives of more. Thank you Miss! Thank you so much!!!"

        "Demand the biiiiig coin.":
            $ goblin_level=min(5, goblin_level+1)
            $ renpy.notify("Goblin instinct +1")

            child "The... coin? Ma'am. This is no regular coin. I need this coin in combination with the crystal."

            pc "Do you know how a store works, little one?"

            child "I do... my tribe would have paid you back. But this is my family's heirloom, infused with magic passed down for generations. I require it desperately."

            pc "This sounds like a you issue. The bills aren't paying themselves, you know?"

            child "I... I suppose there is no other way..."
            play sound sfx_cash

        "Keep the shiny, shinyyyy crystal for yourself.":
            $ goblin_level=min(5, goblin_level+2)
            $ renpy.notify("Goblin instinct +2")

            child "What's the meaning of this, Mister? Aren't you going to sell it to me?"

            pc "I changed my mind. It's no longer for sale. It's mine, I want it."

            child "Don't you have any others-"

            with hpunch
            pc "THEY'RE ALL MINE I TELL YOU!"

            child "Miss... you're scaring me..."

            pc "Leave. Leave now. Store's closed."

            child "What... am I supposed to do now? I failed to find the ingredients... I failed to help mom and dad..."

            pc "Not my circus, not my monkeys. Care to leave now? We're CLOSING."

    play music music_store fadeout 1.0 fadein 1.0

    jump ending




label ending:
    hide screen goblin_hud
    scene black with fade
    pause 1.0
    if goblin_level<=ENDING_HUMAN_MAX:
        jump ending_human
    elif goblin_level>=ENDING_GOBLIN_MIN:
        jump ending_goblin
    else:
        jump ending_indecisive

label ending_human:
    scene bg shop with fade
    show pc human at center with dissolve
    "You have braved your goblin instincts and remained human!"
    jump the_end

label ending_indecisive:
    scene bg shop with fade
    show pc goblin at center with dissolve
    "Congratulations! Your goblin nature is as indecisive as you are!"
    jump the_end

label ending_goblin:
    scene bg shopcursed with fade
    show pc goblin at center with dissolve
    "Congratulations! A bunch of people died, but at least you are a happy goblin!"
    jump the_end

label the_end:
    stop music fadeout 2.0
    scene black with fade
    centered "{size=+10}THE END{/size}"

    return
