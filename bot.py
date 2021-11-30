import discord
from discord.ext import commands
from zipfile import ZipFile
from  niconico_dl  import  NicoNico
import nndownload
import os
from googletrans import Translator
import threading
from secret import TOKEN


##Used for story
import random

##ytmp3 functions
import os
import datetime
from pytube import Playlist,YouTube
import validators
from moviepy.editor import *
### Overwatch
import re
import requests
import json


###############################NICKNAME COMMAND STUFF###################################

#every user in a guild is a 'dork', if a user is in 2 guilds they are
#different 'dorks', thus nicknames are not shared across guilds
class dork:
    def __init__(self,user_id,name,nicknames,guild_id):
        self.user_id=user_id
        self.name = name
        self.guild = guild_id
        self.nicknames=nicknames  #[]
        try:
            self.nicknames.remove('')
        except:
            pass
    def add_nickname(self,new_nick):
        self.nicknames.append(new_nick)
    def remove_nickname(self,to_remove,gid):
        try:
            self.nicknames.remove(to_remove)
            delete_nickname(self.user_id,self.name,to_remove,gid)
            return -1
        except:
            return 0
    def __str__(self):
        return self.user_id +', '+self.name +','+ str(self.nicknames)

#get nicknames from file on bootup, returns a dictionary of userid+guildid:dorkObject
def getNicknames():
    with open("nicknames.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()
    file.close()
    dic={}
    for line in lines:
        props = line.split(',')
        if(len(props) < 2):
            continue
        nicknames = props[2].split(';')#these are the actual nicknames
        dic[int(props[0])+int(props[3])]=dork(props[0],props[1],nicknames, props[3])
    return dic

#add a nickname to someone in the file
def saveNicknames(mid,name,nn,g):
    with open("nicknames.csv", "r", encoding="utf-8") as file:
        lines = file.read().split('\n')
    file.close()
    token=False
    for line in lines:
        words = line.split(',')
        if(len(words) < 3):
            continue
        if words[0] == str(mid) and words[3] == str(g):
            words[2]+=';'+nn
            token=True
            lines.remove(line)
            lines.append(','.join(words))
            break
    if token==False:
        lines.append(str(mid)+','+name+','+nn+','+str(g)+'\n')
    x='\n'.join(lines)
    with open("nicknames.csv", 'w', encoding='utf-8') as f:
        f.write(x)
    f.close()

#Remove a name from the nickname file
def delete_nickname(mid,name,to_remove,g):
    with open("nicknames.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()
    file.close()
    for line in lines:
        words = line.split(',')
        if words[0] == str(mid) and words[3] == str(g):
            nicks = words[2].split(';')
            nicks.remove(to_remove)
            n = ';'.join(nicks)
            new_words = []
            new_words.append(words[0])
            new_words.append(words[1])
            new_words.append(n)
            new_words.append(words[3])
            lines.remove(line)
            lines.append(','.join(new_words))
            break
    x=''.join(lines)
    with open("nicknames.csv", 'w', encoding='utf-8') as f:
        f.write(x)
    file.close

##############################END NICKNAME CODE#################################


##############################YTMP3 CODE########################################

#gotta do this for reasons I'm not totally aware of
def get_playlist_list(url):
    pl = Playlist(url)
    pl._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
    return [l for l in pl]

def mp4_mp3(name,timestamps=[],pname = None):
    clip=VideoFileClip(name)#get mp4 video
    #pname: prefered name, name mp3 file this
    if pname == None or pname == "":
        pname = name
    if(len(timestamps) != 2):
        if(len(timestamps) ==1):#if we only have a start time
            timestamps.append(clip.duration)
        else:#otherwise if we don't have any, or somehow have too many?
            timestamps=["0:00",clip.duration]
        
    audioclip = clip.audio #converts mp4 to mp3
    audioclip=audioclip.subclip(t_start=timestamps[0],t_end=timestamps[1])#get a subclip
    audioclip.write_audiofile(pname + '.mp3', verbose=False,logger = None)#writes to an mp3
    #closes both clips
    clip.close()
    audioclip.close()
    os.remove(name) # deletes mp4 file

def download_mp4s(url):
    #loops because this fails OFTEN because it kinda sucks
    done = False
    counter = 0
    #windows has some picky characters
    forbidden_chars=['<','>',':','"','/','\\','|','?','*']
    while not done and counter<50:
        try:
            yt = YouTube(url)#Get youtube video
            name=yt.title
            for char in forbidden_chars:
                name = name.replace(char,'')#Makes the title valid
            yt.streams.first().download(filename=name)#Download it
            return name
        except:
            return -1

###############ENDS YTMP3 CODE##########################################################


##############################################BOT INITIALIZATION CODE########################
##########Following code based on: https://stackoverflow.com/questions/56796991/discord-py-changing-prefix-with-command

def read_prefixes():
    file = open("prefixes.txt",'r')
    lines=file.read().split('\n')
    file.close()
    prefixes={}
    for line in lines:
        try:
            gid = int(line.split(',')[0])
            prefix=line.split(',')[1]
            prefixes[gid]=prefix
        except:
            print(line)
    return prefixes
              
custom_prefixes = read_prefixes()


#You'd need to have some sort of persistance here,
#possibly using the json module to save and load
#or a database                
default_prefixes = ['!']

async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        return custom_prefixes.get(guild.id, default_prefixes)
    else:
        return default_prefixes

#set up the bot with intents and whatnot
intents = discord.Intents.all()
client = commands.Bot(intents=intents,command_prefix=determine_prefix)

@client.command(brief="sets a custom prefix for the server",
                help="""syntax:
                            !setprefix <prefix>       sets the bot to use a custom prefix""")
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, *, prefixes=""):
    if(not len(prefixes.split(" "))==1):
       await ctx.send("Error, prefixes can not have spaces")
       return
    alterPrefixFile(ctx.guild.id,(prefixes.split() or default_prefixes)[0])
    custom_prefixes[ctx.guild.id] = prefixes.split() or default_prefixes
    await ctx.send("Prefix set!")

def alterPrefixFile(gid,prefix):
    file = open("prefixes.txt",'r')
    lines=file.read().split('\n')#get lines
    file.close()
    found = False
    for line in lines:#iterate through lines
        data=line.split(',')
        if data[0] == str(gid):#if we found the guild id
            found=True
            lines.remove(line)
            data[1]=prefix
            lines.append(",".join(data))#change the prefix
            break
    if not found:#otherwise add it to the end
        lines.append(str(gid)+','+prefix)
    newFile='\n'.join(lines)
    file=open('prefixes.txt','w')#write a new file
    file.write(newFile)
    file.close()
    
######################End taken code########################################

#said when a playlist is uploaded to website
sayings = ["here is the [link](LINK) to your file","I have dumped your file onto [FileDitch](LINK)"]

#get nickname dic
dic = getNicknames();

#get pants dic
file = open('pants.txt', encoding='utf-8')
pants_list = file.read().split('\n')
file.close()

#discord doesnt allow japanese characters, so we have to translate them so they have a title
translator = Translator()

#create a global zip object for threading later
zipObj = None





##############################################END BOT INITIALIZATION CODE########################

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


################################################YTMP3 COMMAND###############################

#!mp3 url -p pname -t timestamp start timestamp end   
@client.command(brief="sends mp3 file from youtube url",
                help="""syntax:
                            mp3 <url> [options]

                        options:
                            -p <name>                     specify what name you want the mp3 file to have
                            -t <start_time> *<end_time>   specify what time(in seconds)the clip should start and end at""")
async def mp3(ctx,*args):
    if(len(args)<1):#maybe call nicknames help function?
        await ctx.send("Error, no url inputted")
        return

    url=args[0]
    pname = ""
    timestamps =[]
    print(url)
    
    if(args.count('-p') >0):#user wants a special name
        name = args[args.index('-p')+1]
        pname = name
    if(args.count('-t') >0):#user wants a subclip of audio
        start = args[args.index('-t')+1]
        try:
           end = args[args.index('-t')+2]
           if(not end == '-p'):
               timestamps = [start,end]
           else:
                timestamps=[start]
        except:
            timestamps = [start]
            
       
    if('youtube' in url or 'youtu.be' in url):
        if('playlist' in url):
            await sendPlaylist(ctx,url,pname,timestamps)
        else:
            await sendVideo(ctx,url,pname,timestamps)
    elif('nicovideo' in url):
        await sendNicoVideo(ctx,url,pname,timestamps)
           
#send a playlist to someone   
async def sendPlaylist(ctx,url,pname,timestamps):
    global zipObj
    await ctx.send("getting mp3(s), this will take a bit, especially for large playlists")
    zipObj = ZipFile('songs.zip', 'w')         #make zip file
    urls=get_playlist_list(url)
    lock = threading.Lock()
    threads=[]
    for url in urls:
        new_thread = threading.Thread(target=multiThreadDownload, args=(url,lock,))
        new_thread.start()
        threads.append(new_thread)
    for t in threads:
        t.join()
       
            
    zipObj.close()                     ##close zip       
    url = "https://up1.fileditch.com/upload.php"     ##upload link to file website
    file = open("songs.zip", "rb")                        ##opens the file
    response = requests.post(url, files = {"files[]": file})     ##response in text
    file.close()
    response_json = json.loads(response.text)
##    print(response_json)
    if(not response_json["success"]==True):
        await ctx.send("error uploading to website")
        return
    response_url=response_json["files"][0]["url"]
    embed = discord.Embed()
    words = random.choice(sayings)
    words = words.replace("LINK",response_url)
    embed.description = words
    await ctx.send(embed = embed)

def multiThreadDownload(url,lock):
    global zipObj
    name=download_mp4s(url)
    if not name == -1:
        mp4_mp3(name,[])
        lock.acquire()
        zipObj.write(name+'.mp3')## add file to zip
        lock.release()
        os.remove(name+'.mp3')

#User wants one video              
async def sendVideo(ctx,url,pname,timestamps):
    await ctx.send("getting mp3")
    name = download_mp4s(url)
    if name ==-1:
      await ctx.send("error, video not found, please try again")
      return
    if(pname==""):
        pname = name
    mp4_mp3(name,timestamps,pname)
    f = open(pname+'.mp3',"rb")
    file = discord.File(f,pname+".mp3")
    await ctx.send(file=file)
    f.close()
    os.remove(pname+'.mp3')
    
async def sendNicoVideo(ctx,url,pname,timestamps):
    await ctx.send("getting mp3")
    #https://www.nicovideo.jp/watch/sm28649562
    
    number = url.split('/')[-1]
    niconico = NicoNico(number)#get video data
    title = niconico.data["video"]["title"]


    forbidden_chars=list('<>:"/\|?*')#make it a legal filename
    for char in forbidden_chars:
        title=title.replace(char,'')
    
    title = translator.translate(title).text#get a new title since discord has no japanese chars for filanames
    nndownload.execute("-g", "-o",title,'-q','-r 5', url)
    mp4_mp3(title,timestamps,pname)
    
    if(pname==""):
        pname = title
    
    f = open(pname+'.mp3',"rb")
    file = discord.File(f,pname+".mp3")
    await ctx.send(file=file)
    f.close()
    os.remove(pname+'.mp3')
##############################END YTMP3 COMMAND###################################


######################################NICKNAME COMMAND#####################################
@client.command(brief="allows for additional nicknames for members",
                help="""syntax:
                        nickname:                              shows all of your nicknames on this server
                        nickname <member>:                     shows all of that member's nickname on this server
                        nickname <member> add <nickname>:      adds a nickname to that member
                        nickname <member> remove <nickname>:   removes a nickname from a user (only for self or admins)""")
async def nickname(ctx,*args):
    if(len(args)==0):#send author's nicknames
        member = ctx.message.author
        await sendNickname(ctx,member)
        return
    elif(len(args)==1):# this means looking at nicknames for a particular user
        member=ctx.guild.get_member_named(args[0])
        await sendNickname(ctx,member)
        return

    
    #I've made it so that, theorhetically commands can be added in any order
    #to do this we must know the index of the command and member name
    member_num=-1
    for i in range(len(args)):
        member=ctx.guild.get_member_named(args[i])
        member_num=i
        
        if(member):
            break
    if(member_num ==-1):
        await message.channel.send("error, no user found")
    
    if(args.count('add')):#we wanna add

        #everything left over is part of the nickname
        nickname_list = list(args)
        nickname_list.remove('add')
        nickname_list.remove(args[member_num])
        nickname = ' '.join(nickname_list).strip(',')
        try:
            #if user already in csv file
            key = member.id+ctx.guild.id
            x=dic[key]
            x.add_nickname(nickname)
            saveNicknames(member.id,member.name,nickname,ctx.guild.id)
        except:
            #otherwise add them
            dic[key]=dork(key,member.name,([nickname]),ctx.guild.id)
            saveNicknames(member.id,member.name,nickname,ctx.guild.id)
        await ctx.send("nickname added")
        await sendNickname(ctx,member)
        
    elif(args.count('remove')): 
        #everything left over is part of the nickname
        nickname_list = list(args)
        nickname_list.remove('remove')
        nickname_list.remove(args[member_num])
        nickname = ' '.join(nickname_list).strip(',')

        #only user or admin can remove nickname
        roles = ctx.message.author.roles
        admin = False
        for role in roles:
            if role.permissions.administrator:
                admin = True
        if member == ctx.message.author or admin:
            try:
                key = member.id+ctx.guild.id#get nicknames
                x=dic[key]
                y=x.remove_nickname(nickname,ctx.guild.id)#returns 0 if it errors
                if y==0:
                    await ctx.send("error, nickname not found")
                else:
                    await ctx.send("nickname deleted")
                    await sendNickname(ctx,member)
            except:
                await ctx.send("error, user has no nicknames")
        else:
            await ctx.send("error, only user with nickname, or admin can delete nicknames")

            
    
async def sendNickname(ctx,member):
        try:
            key = member.id+ctx.guild.id
            to_say = member.name +'\n'
            for nickname in (dic[key].nicknames):
                to_say+=nickname+'\n'
            await ctx.send(to_say)
            return
        except:
            await ctx.send(member.name)
            return
##################################END NICKNAME COMMAND#####################################    


###################################MISC COMMANDS########################################
@client.command(brief="generates a random story from inputted words",
                help="""syntax:
                        story <words>:                 generates a random story from selected words
                        story <words> <num_words>:     generates a random story with a word count of num_words
                        story <words>:                 MAX generates a random story with maximum length possible""")
async def story(ctx,*args):
    words=list(args)
    try:
        length = int(args[-1])
        print(length)
        words.pop(-1) #remove number
    except:
        if(args[-1]=='MAX'):
            length = 1000 # if max, they want the maximum length, so thats 1000 words plus 1000 spaces at minimum
            words.pop(-1) #remove MAX
        else:
            length = 50#default to 50 words
    
    my_str=""
    for i in range(length):
        choice = random.randint(0,len(words)-1)
        my_str += words[choice] +' '
        if(len(my_str)>2000):
            my_str=my_str[:2000]#cut down to max length
            break
    await ctx.send(my_str)


@client.command(brief="repeats a phrase a number of times",
                help="""syntax:
                        repeat <phrase>           repeats a phrase 50 times
                        repeat <phrase> <num>     repeats a phrase num times
                        repeat <phrase> MAX       repeats a phrase the maximum message length""")
async def repeat(ctx,*args):
    words=list(args)
    try:
        length = int(args[-1])
        print(length)
        words.pop(-1) #remove number
    except:
        if(args[-1]=='MAX'):
            length = 1000 # if max, they want the maximum length, so thats 1000 words plus 1000 spaces at minimum
            words.pop(-1) #remove MAX
        else:
            length = 50#default to 50 words
    my_str=""
    phrase = ' '.join(words)
    for i in range(length):
        my_str += phrase+' '
        if(len(my_str)>2000):
            my_str=my_str[:2000]#cut down to max length
            break
    await ctx.send(my_str)
###################################END MISC COMMANDS########################################




    
client.run(TOKEN);
