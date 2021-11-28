import discord
from discord.ext import commands
from zipfile import ZipFile
from  niconico_dl  import  NicoNico
import nndownload
import os
from googletrans import Translator
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
### valorant
##import valorant as valorant

sayings = ["nice [cockfile](LINK).","here's your [cockfile](LINK).","one hot steamy load of [cockfile](LINK) here for you",
           "here's your link to the [totally normal file hosting website](LINK)", "this [cockfile](LINK) holds what you seek",
           "pee is stored in the ballfile and the zip link is stored in the [cockfile](LINK)"]

intents = discord.Intents.all()
client = discord.Client(intents=intents)

class dork:
    def __init__(self,user_id,name,nicknames,guild_id):
        self.user_id=user_id
        self.name = name
        self.guild = guild_id
        self.nicknames=nicknames  #[]
        print(self.nicknames)
        try:
            self.nicknames.remove('')
        except:
            pass
    def add_nickname(self,new_nick):
        self.nicknames.append(new_nick)
        print(self.nicknames)
    def remove_nickname(self,to_remove):
        try:
            self.nicknames.remove(to_remove)
            delete_nickname(self.user_id,self.name,to_remove)
            return -1
        except:
            return 0
    def __str__(self):
        return self.user_id +', '+self.name +','+ str(self.nicknames)

def getNicknames():
    with open("nicknames.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()
    file.close()
    dic={}
    for line in lines:
        props = line.split(',')
        if(len(props) < 2):
            continue
        nicknames = props[2].split(';')
        dic[int(props[0])+int(props[3])]=dork(props[0],props[1],nicknames, props[3])
    return dic

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
            print(g)
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

def delete_nickname(mid,name,to_remove):
    with open("nicknames.csv", "r", encoding="utf-8") as file:
        lines = file.readlines()
    file.close()
    for line in lines:
        words = line.split(',')
        if words[0] == str(mid):
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

#############################following code taken from your other ytmp3 py file###################################
def get_playlist_list(url):
    pl = Playlist(url)
    pl._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
    return [l for l in pl]

def mp4_mp3(name,times = [],pname = None):
        print("converting")
##    try:
        if(len(times)==2): #have to get specific times
            clip=VideoFileClip(name)#get mp4 video
            audioclip = clip.audio #converts mp4 to mp3
            audioclip=audioclip.subclip(t_start=times[0],t_end=times[1])
            audioclip.write_audiofile(name + '.mp3', verbose=False,logger = None)#writes to an mp3
            #closes both clips
            clip.close()
            audioclip.close()
            os.remove(name) # deletes mp4 file

        else:
            clip=VideoFileClip(name)#get mp4 video
            audioclip = clip.audio #converts mp4 to mp3
            
            if not pname == None:
                audioclip.write_audiofile(pname + '.mp3', verbose=False,logger = None)#writes to an mp3
            else:
                audioclip.write_audiofile(name + '.mp3', verbose=False,logger = None)#writes to an mp3
            #closes both clips
            clip.close()
            audioclip.close()
            os.remove(name) # deletes mp4 file
        
##    except:
##        try:
##            os.remove(name+'.mp4')
##            print("Error with "+name+" May have no audio, if not contact Emily (Emilbee#9025 on discord)")#no clue if this ever fires, if it does contact me
##        except:
##            print("Error with "+name+" May have no audio, if not contact Emily (Emilbee#9025 on discord)")

def download_mp4s(url):
    print("downloading mp4")
    #loops because this fails OFTEN because it kinda sucks
    done = False
    counter = 0
    #windows has some picky characters
    forbidden_chars=[",","～","-","☺","☻","♥","♦","♣","♠","•","◘","○","◙","♂","♀","♪","♫","☼","►","◄","↕","‼","¶","§","▬","↨","↑","↓","→","←","∟","↔","▲","▼",'+','~','#','<','>','%','&','*','{','?','}','/','\\','$','+','!',"'",'|','`','"','=',':','@','.']
    while not done and counter<50:
        try:
            yt = YouTube(url)#Get youtube video
            name=yt.title
            for char in forbidden_chars:
                name = name.replace(char,'')#Makes the title valid
            yt.streams.first().download(filename=name)#Download it
            return name
        except:
            print("Response timed out, trying again")
            counter+=1
            if counter >=10:
                print("huh, video may not exist, will exit when counter = 50. counter at: ",counter)
    print("error, infinite loop, video may be private or a livestream")
    name='ERRORnotAVidEoTitlE'#this is stupid but you're too lazy to fix it
    return name#returns name
############################End taken code######################################################################

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

dic = getNicknames();
riot_key ="RGAPI-3698ac85-81e0-4abd-80c1-e50e35859408"
##val = valorant.Client(riot_key, locale="en-US")
file = open('pants.txt', encoding='utf-8')
pants_list = file.read().split('\n')
file.close()
translator = Translator()

@client.event
async def on_message(message):
    if message.author == client.user:      #So bot doesnt react to itself ever
        return
    line = message.content
    if("!OW" in line):
        words = line.split(' ')
        try:
            name = words[1]
        except:
            await message.channel.send("ERROR, enter a person")
            return
        r = requests.get('https://owapi.io/profile/pc/us/'+name)
        jsonObject = r.json()
        comp = jsonObject['competitive']
        support = comp['support']
        tank = comp['tank']
        dps = comp['damage']

        a = tank['rank']
        b = dps['rank']
        c = support['rank']

        await message.channel.send("Tank: "+str(a)+' / '+"DPS: "+str(b)+' / '+"support: "+str(c))
    if('!pants' in line):
        choice = random.randint(0,len(pants_list)-1)
        await message.channel.send(pants_list[choice])

#####################turns out valorant api kinda sucks#############################
##    if("!VAL" in line):
##        words = line.split(' ')
##        try:
##            name = words[1]
##        except:
##            await message.channel.send("ERROR, enter a person")
##            return
##        user = val.get_user_by_name(name, delim="#")
##        t= val.get_acts()
##        print(t)
#####################################################################################
    if("!help" in line):
        string = "**COMMANDS:**\n"
        string+="!nickname: add/remove/display nicknames, type **!nickname help** for more info\n"
        string+="!mp3 [url]: uploads an mp3 file from a youtube url [!mp3 https:\//www.youtube.com/watch?v=5PyYvLYWUQM]\n"
        string+="!r text *int:repeats text over for int specified times, if blank it defaults to 50, if MAX outputs max amount of times\n"
        string+="!story text *int: randomy chooses words from text and puts them into a sentence of size int, by default int is set to 50"
        await message.channel.send(string)
    if("!mp3" in line):
        print("get video")
        words = line.split(' ')
        print(words)
        nameFlag=False;
        try:
            url = words[1]
        except:
            await message.channel.send("ERROR, not a url numbnuts")
            return
        times=[]
        if(len(words) > 2 and words[2]=="-t"):
            print("got times")
            times.append(words[3])
            times.append(words[4])
        elif(len(words)>2):
            pname = words[2];
            nameFlag=True;
        
            
            
        valid=validators.url(url)
        if not (valid==True):
            await message.channel.send("ERROR, not a url numbnuts")
        else:
            if 'youtu.be' in url or 'youtube' in url:
                if "playlist" in url:
                    await message.channel.send("getting mp3(s), this will take a bit, especially for large playlists") ##say this
                    counter=0
                    valid = False
                    names = []
                    zipObj = ZipFile('songs.zip', 'w')         #make zip file
                    while counter<50 and not valid:          ##try not to error
                        urls=get_playlist_list(url)
                        counter+=1
                        for url in urls:
                            valid = True
                            name=download_mp4s(url)
                            if not name == 'ERRORnotAVidEoTitlE':
                                names.append(name)
                                mp4_mp3(name,[])
                                zipObj.write(name+'.mp3')                                   ## add file to zip
                                print("downloaded "+name)
                        zipObj.close()                                                              ##close zip
                        ##x = os.system('curl -i -F files[]=@songs.zip https://cockfile.com/upload.php')          ##say this in command line to send file to cockfile
                        url = "https://cockfile.com/upload.php"                            ##upload link to cockfile
                        file = open("songs.zip", "rb")                                     ##opens the file
                        response = requests.post(url, files = {"files[]": file})           ##response in text
                        penishats = response.text.split('\n')[6]                           ##get url from response
                        file.close()
                        print(penishats)                                                        ##print url
                        penishats = penishats.split('"')
                        embed = discord.Embed()
                        words = random.choice(sayings)
                        words = words.replace("LINK",penishats[3])
                        embed.description = words
                        await message.channel.send(embed = embed)
                        for n in names:
                            os.remove(n+'.mp3')


                else: #TODO
                    await message.channel.send("getting mp3")
                    name = download_mp4s(url)
                    print(name)
                    if name =='ERRORnotAVidEoTitlE':
                      valid = False
                    if not valid:
                      await message.channel.send("error, video not found, please try again")
                    else:
                      if nameFlag:
                          mp4_mp3(name,times,pname)
                          f = open(pname+'.mp3',"rb")
                          file = discord.File(f,pname+".mp3")
                          await message.channel.send(file=file)
                          f.close()
                          os.remove(pname+'.mp3')
                      else:
                          mp4_mp3(name,times)#changes mp4 to mp3 and deletes mp4
                          f = open(name+'.mp3',"rb")
                          file = discord.File(f,name+".mp3")
                          await message.channel.send(file=file)
                          f.close()
                          os.remove(name+'.mp3')
                      
            elif 'nicovideo' in url:
                await message.channel.send("getting mp3")
                #https://www.nicovideo.jp/watch/sm28649562
                number = url.split('/')[4]
##                print(number)
                niconico = NicoNico(number)
                title = niconico.data["video"]["title"]
##                print(title)


                forbidden_chars=list('<>:"/\|?*')
                for char in forbidden_chars:
                    title=title.replace(char,'')

##                file = open(title+'.mp4','w')
##                file.write(' ')
##                file.close()
                title = translator.translate(title).text
                nndownload.execute("-g", "-o",title+'.mp4','-q','-r 5', url)
                mp4_mp3(title,[])
                f = open(title+'.mp3',"rb")
                file = discord.File(f,title+".mp3")
                await message.channel.send(title,file=file)
                f.close()
                os.remove(title+'.mp3')

                print('done')



    if '!r' in line:
        try:
            maximize = False
            words = line.split(' ')
            try:
                l = int(words[-1]) #get words
                words.pop(-1) #remove number
            except:
                l = 50
                if(words[-1] == 'max'):
                    maximize = True
                    words.pop(-1)
            words.pop(0) #remove command
            counter = 0
            to_say = ' '.join(words)
            my_str = ""
            if maximize:
                while len(my_str) < 2000 - len(to_say):
                    my_str += to_say +' '
            else:
                while counter < l: #this is L not 1
                    counter +=1
                    my_str += to_say + " "
            await message.channel.send(my_str)
        except:
            await message.channel.send("ERROR")
    if '!story' in line:
        try:
            words = line.split(' ')
            try:
                l = int(words[-1]) #get words
            except:
                l = 50
            words.pop(0) #remove command
            words.pop(-1) #remove number
            counter = 0
            my_str = ""
            while counter < l: #this is L not 1
                choice = random.randint(0,len(words)-1)
                counter +=1
                my_str += words[choice] + " "
            await message.channel.send(my_str)
        except:
            await message.channel.send("ERROR,message too long (probably)")
    ### THE NICKNAME SAGA####################################################
    if '!nickname' in line:
        guild_id = message.guild.id
        g = client.get_guild(guild_id)
        x = g.members
        words = message.content.split(' ')
        if len(words) >= 3:
            if words[2] == 'add':
                nic =""
                for i in range(3,len(words)):
                    nic += words[i]+' '
                member = g.get_member_named(words[1])
                if member == None:
                    await message.channel.send("error, no user named "+words[1])
                else:
                    try:
                        #if user already in csv file
                        key = member.id+guild_id
                        x=dic[key]
                        x.add_nickname(nic)
                        saveNicknames(member.id,member.name,nic,guild_id)
                    except:
                        #otherwise add them
                        dic[key]=dork(key,member.name,([nic]),guild_id)
                        saveNicknames(member.id,member.name,nic,guild_id)
                    await message.channel.send("nickname added")

            elif words[2] == 'remove': #Remove nickname
                nic =""
                for i in range(3,len(words)): #get nickname to remove
                    nic += words[i]+' '
                member = g.get_member_named(words[1])
                if member == None:
                    await message.channel.send("error, no user named "+words[1])
                else:
                    roles = message.author.roles
                    admin = False
                    for role in roles:
                        if role.permissions.administrator:
                            admin = True
                    if member == message.author or admin:
                        try:
                            key = member.id+guild_id
                            x=dic[key]
                            y=x.remove_nickname(nic)
                            if y==0:
                                await message.channel.send("error, nickname not found")
                            else:
                                await message.channel.send("nickname deleted")
                        except:
                            await message.channel.send("error, user has no nicknames")
                    else:
                        await message.channel.send("error, only user with nickname, or admin can delete nicknames")

            else:
                await message.channel.send("command not recognized, please say !nicknames [name] to display nicknames, or !nicknames [name] add [nickname] to add a nickname")
        elif len(words) ==2:
            if words[1] == 'help':
                await message.channel.send("commands:\n!nicknames - prints out all your current nicknames\n!nicknames [NAME] - prints out all the nicknames of [NAME]\n!nicknames [NAME] add [NICKNAME] - adds a nickname to a user\n!nicknames [NAME] remove [NICKNAME] - removes a nickname of a user (only can be done by admins or person with nickname trying to be removed)\nngl sometimes it fucks up and you end up with duplicate nickanes, its a feature")
            else:
                member=g.get_member_named(words[1])
                if member == None:
                    await message.channel.send("error, no user named "+words[1])
                else:
                    try:
                        key = member.id+guild_id
                        to_say = member.name +'\n'
                        for nickname in (dic[key].nicknames):
                            to_say+=nickname+'\n'
                        await message.channel.send(to_say)
                    except:
                        await message.channel.send(member.name)
        elif len(words)==1:
            member = message.author
            try:
                key = member.id+message.guild.id
                to_say = member.name +'\n'
                for nickname in (dic[key].nicknames):
                    to_say+=nickname+'\n'
                await message.channel.send(to_say)
            except:
                await message.channel.send(member.name)




client.run(TOKEN)
