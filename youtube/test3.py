from Tkinter import *
from bs4 import BeautifulSoup
import re
import requests


def channelInfo():
   Link = link.get()
   r = requests.get(Link)
   soup = BeautifulSoup(r.content)
   channelName = "Channel Name: " + soup.title.string
   firrt = Label(text=channelName,fg='yellow',bg='black').place(x=0,y=0)
   var = None
   var1 = None
   var3 = None
   var4 = None
   placer =0
   placer1 =0
   adjust = 0
   for i in soup.find_all('a',class_="yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2"):
       var = i.text
       second = Label(text=var,fg='black',bg='white').place(x=200,y=40+adjust)
       adjust+=20
   desc = soup.find_all(attrs={"name":"description"})
   DESC = desc[0]['content'].encode('utf-8')
   third = Label(text=DESC,fg='black',bg='yellow').place(x=0,y=20)
   for j in soup.find_all('li'):
         var1=j.text
         varr = re.findall('[0-9]+,[0-9]+ views',var1)
         for views in varr:
               var3 = Label(text=views,fg='blue').place(x=650,y=40+placer)
               placer+=20
   for k in soup.find_all('a',class_="yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2"):
      links = k.get("href")
      final = Link+links
      var4 = Label(text=final).place(x=750,y=40+placer1)
      placer1+=20



gui = Tk()
gui.geometry('500x400')
gui.title('The Youtube Crawler')
label = Label(text='Paste the link below to crawl Youtube',fg='blue')
label.pack()
link = StringVar()
entry = Entry(gui,textvariable=link)
entry.pack()
channel = Button(text='Crawl this channel',fg='white',bg='black',width=30,command=channelInfo)
channel.place(x=10,y=45)
'''
specific = Button(text='Inform about this video',fg='black',bg='white',width=30)
specific.place(x=270,y=45)
'''
entry.focus_set()
url = entry.get()
gui.mainloop()