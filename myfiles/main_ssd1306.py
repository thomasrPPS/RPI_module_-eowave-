from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306,sh1106,ssd1327,ssd1322_nhd
from pathlib import Path
#import board
import time
import spidev
from PIL import Image,ImageDraw, ImageFont

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio

import argparse
from math import *
import random

import graphics
import icones
import cfg
#import psutil
#import serial_in

SAVER_SCREEN = 1234560
SAVER_SCREEN2 = -1
MAIN_MENU = 0
LIST_SCREEN = 1
POT_SCREEN = 2
SLIDER_SCREEN = 3
VIEW_ADSR = 4
VIEW_TAB = 5
CV_SCREEN = 6
MIDI_SCREEN = 7
CPU_SCREEN = 8
WIFI_SCREEN = 9
LIST_PRESET = 10
SAVE_PRESET = 11
#DRAW_SCREEN = 9
#VIEW_WAVE= 8
#STATS = 10

actual_value=0
adsr = [0] * 4 
sliders = [0] * 4 
pots = [0] * 4 
waveform= [0] * 256 
#textfields=["none"] * 20
#potvalues=[63] * 20 
patchlist=["EMPTY1","EMPTY2","EMPTY3","EMPTY4","EMPTY5","EMPTY6","EMPTY7","EMPTY8","EMPTY9","EMPTY10","EMPTY11","EMPTY12","EMPTY13"] 
presetlist=["EMPTY1","EMPTY2","EMPTY3","EMPTY4","EMPTY5","EMPTY6","EMPTY7","EMPTY8","EMPTY9","EMPTY10","EMPTY11","EMPTY12","EMPTY13"] 
midiList=[]
midiSelect=[]


potlabel=["empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty","empty"]
tab_icones=[icones.files,icones.pot,icones.slider,icones.env,icones.rand,icones.cv,icones.midi,icones.cpu,icones.wifi,icones.loading,icones.saw,icones.tri]

selected_page=0
sel_page = -1
sel_menu = 0
nb_pages = 4
MAX_MENU = 8
wavebar = 0
selected_patch = 0
selected_preset = 0
save_preset = 0
selected_midi = 0
#max_files = 8
screen_mode=1
counter = 0
BLACK="black"
WHITE="white"
#GREY=(60,60,60)
#GREY3=(40,40,40)
#GREY2=(30,30,30)
#G1=(20,20,20)
#G2=(30,30,30)
#G3=(40,40,40)
GREY="white"
GREY3="white"
GREY2="white"
G1="white"
G2="white"
G3="white"
update=0
new = 0
coor=(0,0,0,0)
dtype="rect"
selected_color =[G3] * 12
width =128
height =64
FONTSIZE = 12
list_offset=0
big_val=0
cv=[0,0]
gate=[0,0]
cpu="... %"
ssid=""
ipadress=""
font_b = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE+10)
#font = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE)
font = ImageFont.load("/home/pi/myfiles/fonts/bitocra7.pil")
#font_s = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE-1)
#font_s2 = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE-2)

#img_1 = Image.open('/home/pi/myfiles/fonts/c.gif')

for x in range(128):
    waveform[x]=x/2

# rev.1 users set port=0
 #substitute spi(device=0, port=0) # below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = spi(device=0, port=0,gpio_DC=23) 
#serial = i2c(port=1, address=0x3C)
# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)
#device = sh1106(serial)
#device = ssd1322_nhd(serial, width=128, height=64)

# demmarage de PD
cfg.start_pd()
patchlist=cfg.readPatchList(0)
parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=5006,help="The port the OSC server is listening on")
args = parser.parse_args()
client = udp_client.SimpleUDPClient(args.ip, args.port)
client.send_message("/test", "hello")

def set_panel(unused_addr, *args):
  global max_files
  global selected_patch
  global selected_preset
  global save_preset
  global selected_midi
  global patchlist
  global presetlist
  global sel_menu
  global sel_page
  
  patch_len= len(patchlist)
  preset_len= len(presetlist)
  print (args[0])
  

  if (sel_page==LIST_SCREEN):
    print("list screen")
    if args[0]=="UP" and selected_patch < patch_len-1:
      selected_patch=selected_patch+1
      #if selected_patch >= patch_len: selected_patch=patch_len-1

    elif args[0]=="DOWN" and selected_patch >0:
      selected_patch=selected_patch-1
      #if selected_patch <0: selected_patch=0
    
    elif args[0]=="ENTER":
      client.send_message("/load", patchlist[selected_patch])
      presetlist=cfg.readPresetList(patchlist[selected_patch])
      sel_page= POT_SCREEN
    elif args[0]=="ESC":
      sel_page= 0
  elif (sel_page==LIST_PRESET):
    if args[0]=="UP":
      selected_preset=selected_preset+1
      if selected_preset >= preset_len: selected_preset=preset_len-1

    elif args[0]=="DOWN":
      selected_preset=selected_preset-1
      if selected_preset <0: selected_preset=0
    
    elif args[0]=="ENTER":
      print("envoi osc")
      client.send_message("/preset", presetlist[selected_preset])
      client.send_message("/menu", 0)
      sel_page= POT_SCREEN
    elif args[0]=="ENTER_HOLD":
      sel_page= SAVE_PRESET
      client.send_message("/menu", 11)
    elif args[0]=="ESC":
      sel_page= POT_SCREEN
  
  elif (sel_page==SAVE_PRESET):
    if args[0]=="UP":
      save_preset=save_preset+1
      if save_preset >= preset_len: save_preset=preset_len-1

    elif args[0]=="DOWN":
      save_preset=save_preset-1
      if save_preset <0: save_preset=0
    
    elif args[0]=="ENTER":
      print("envoi osc")
      client.send_message("/preset_save", presetlist[save_preset])
      client.send_message("/menu", 0)
      sel_page= POT_SCREEN
    elif args[0]=="ESC":
      sel_page= POT_SCREEN
      
  elif (sel_page==MAIN_MENU):
    if args[0]=="UP":
      sel_menu=sel_menu+1
      if sel_menu >= MAX_MENU: sel_menu= MAX_MENU
    elif args[0]=="DOWN":
      sel_menu=sel_menu-1
      if sel_menu <0: sel_menu=0
    elif args[0]=="ENTER":
      sel_page=sel_menu+1
      if sel_page == POT_SCREEN:
        client.send_message("/menu", 0)
      elif sel_page == SLIDER_SCREEN:
        client.send_message("/menu", 1)
      elif sel_page == VIEW_ADSR:
        client.send_message("/menu", 2)
      elif sel_page == VIEW_TAB:
        client.send_message("/menu", 3)
      elif sel_page >= CV_SCREEN and sel_page <= WIFI_SCREEN:
        client.send_message("/param",sel_page)
  elif (sel_page==CV_SCREEN):
    if args[0]=="ESC":
      sel_page=0
  elif (sel_page==MIDI_SCREEN):
    if args[0]=="UP":
      selected_midi=selected_midi+1
      if selected_midi >= len(midiList): selected_midi=len(midiList)-1
    elif args[0]=="DOWN":
      selected_midi=selected_midi-1
      if selected_midi <0: selected_midi=0
    elif args[0]=="ENTER":
      midiSelect[selected_midi]=not(midiSelect[selected_midi])
      if midiSelect[selected_midi]==True:
        command= "aconnect "+midiList[selected_midi][:midiList[selected_midi].find(":")]+":0 128:0"
      else:
        command= "aconnect -d "+midiList[selected_midi][:midiList[selected_midi].find(":")]+":0 128:0"
      cfg.command(command)
      print(command)
    elif args[0]=="ESC":
      sel_page=0
  elif (sel_page==CPU_SCREEN):
    if args[0]=="ESC":
      sel_page=0
  elif (sel_page==WIFI_SCREEN):
    if args[0]=="ESC":
      sel_page=0
  elif (sel_page==POT_SCREEN):
    if args[0]=="ESC":
      sel_page=1
    elif args[0]=="UP":
      client.send_message("/menu", 1)
      sel_page=SLIDER_SCREEN
    elif args[0]=="ENTER":
      sel_page=LIST_PRESET
      client.send_message("/param",sel_page)
  elif (sel_page==SLIDER_SCREEN):
    if args[0]=="ESC":
      sel_page=1
    elif args[0]=="DOWN":
      client.send_message("/menu", 0)
      sel_page=POT_SCREEN
    elif args[0]=="UP":
      client.send_message("/menu", 2)
      sel_page=VIEW_ADSR
    elif args[0]=="ENTER":
      sel_page=LIST_PRESET
      client.send_message("/param",sel_page)
  elif (sel_page==VIEW_ADSR):
    if args[0]=="ESC":
      sel_page=1
    elif args[0]=="DOWN":
      client.send_message("/menu", 1)
      sel_page=SLIDER_SCREEN
    elif args[0]=="UP":
      client.send_message("/menu", 3)
      sel_page=VIEW_TAB
    elif args[0]=="ENTER":
      sel_page=LIST_PRESET
      client.send_message("/param",sel_page)
  elif (sel_page==VIEW_TAB):
    if args[0]=="ESC":
      sel_page=1
    elif args[0]=="DOWN":
      client.send_message("/menu", 2)
      sel_page=VIEW_ADSR
    elif args[0]=="ENTER":
      sel_page=LIST_PRESET
      client.send_message("/param",sel_page)


def set_mode(unused_addr, *args):
  global screen_mode
  print (args)
  screen_mode=args[0]

def draw_rect(unused_addr, *args):
  global new
  global coor
  global dtype
  new=1
  coor=args
  dtype = "rect"
def draw_circle(unused_addr, *args):
  global new
  global coor
  global dtype
  new=1
  coor=args
  dtype = "circle"

def draw_fill(unused_addr, *args):
  global new
  global coor
  global dtype
  new=1
  coor=args
  dtype="list"

def set_adsr(unused_addr, *args):
  global adsr
  adsr=args
 # print (adsr)

def set_sliders(unused_addr, *args):
  global sliders
  sliders=args
  print (sliders)
 
def set_pots(unused_addr, *args):
  global pots
  pots=args

def set_update(unused_addr, *args):
  global update
  update=1
  #print("update : ",update)

def set_page(unused_addr, *args):
  global sel_page
  #print (args)
  sel_page=int(args[0])

def set_waveform(unused_addr, *args): #must be 128
  global waveform
  for i in range(128):
    waveform[i]=args[i]
  #print(waveform)
def set_waveform2(unused_addr, *args): #must be 128
  global waveform
  for i in range(256):
    waveform[i]=args[i]
  #print(waveform)
def set_wavebar(unused_addr, *args): #must be 128
  global wavebar
  wavebar=args[0]

def set_values(unused_addr, *args):
  global actual_value
  actual_value=int(args[0])
  print(actual_value)
  
def set_pots_labels(unused_addr, *args):
  global potlabel
  temp=0
  for temp in range(16):
    if isinstance(args, str) and temp < len(args):
      potlabel[temp]=args[temp]
    elif temp<len(args):
      potlabel[temp]=str(args[temp])
    else:
      potlabel[temp]="empty"

def set_cpu(unused_addr, *args):
  global cpu
  cpu = str(int(args[0]))+" %"

def set_midi(unused_addr, *args):
  global midiList
  midiList = cfg.getMidiList()
  for i in range(len(midiList)):
    midiSelect.append(False)
  
def set_cv_gate(unused_addr, *args):
  global cv
  global gate
  if args[0]== 0:
    gate[0]=args[1]
  elif args[0]== 1:
    gate[1]=args[1]
  elif args[0]== 2:
    cv[0]=args[1]
  elif args[0]== 3:
    cv[1]=args[1]
      

async def update_screen():
  global potvalues
  global sel_page
  global waveform
  global adsr
  global selected_color
  global sel_menu
  global width
  global height
  global update
  global actual_value

  global new
  global coor
  global dtype
  global wavebar
  
  global ssid
  global ipadress

  x1=40
  x2=13
  y1=32
  z=0
  dirx1=1
  diry1=1
  
  rayon=6
  while True:
   
    if sel_page == SAVER_SCREEN:
      with canvas(device) as draw:
       # print("AA")
        x1=x1+dirx1
        y1=y1+diry1
      
        if x1>(width-rayon): dirx1=-dirx1
        if x1<rayon: dirx1=-dirx1
        if y1>(height-rayon): diry1=-diry1
        if y1<rayon: diry1=-diry1
        draw.ellipse((x1-rayon,y1-rayon,x1+rayon,y1+rayon) , outline=WHITE, fill=GREY3, width=1)
        await asyncio.sleep(0.04)
        
    if sel_page == SAVER_SCREEN2:
      with canvas(device) as draw:
       # print("AA")
        if x2 <118:
          x2+=1
        draw.rectangle((10,40,118,30), outline=WHITE, fill=0)
        draw.rectangle((10,40,x2,30), outline=WHITE, fill=1)
        await asyncio.sleep(0.01)
         
    elif sel_page == POT_SCREEN:
      with canvas(device) as draw:
       # print("BB")
        graphics.title(draw,'POTS')
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        for p in range(4):
          graphics.pot(draw,p,potlabel[p],pots[p]/63)
        for i in range(4):
          if i == 0:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=1)
          else:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)

     # draw.rectangle((2,2,126,126), fill=None, outline=G1, width=1)

    elif sel_page == LIST_SCREEN :
      with canvas(device) as draw:
        graphics.title(draw,'SELECT FILE')
      #  draw.rectangle((2,2,126,126), fill=None, outline=G2, width=1)
        graphics.file_display(draw,patchlist,selected_patch,0)
      await asyncio.sleep(0.04)

    elif sel_page == LIST_PRESET :
      with canvas(device) as draw:
        graphics.title(draw,'SELECT PRESET')
       # draw.rectangle((2,2,126,126), fill=None, outline=G2, width=1)
        graphics.file_display(draw,presetlist,selected_preset,0)
      await asyncio.sleep(0.04)
      
    elif sel_page == SAVE_PRESET :
      with canvas(device) as draw:
        graphics.title(draw,'-----------SAVE PRESET-----------')
       # draw.rectangle((2,2,126,126), fill=None, outline=G2, width=1)
        graphics.file_display(draw,presetlist,save_preset,0)
      await asyncio.sleep(0.04)

    elif sel_page == SLIDER_SCREEN:
      with canvas(device) as draw:
        graphics.title(draw,'SLIDERS')
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        draw.line((width/2+20,7,width/2+20,height),fill=WHITE)
        draw.text((width/2 +24,17),potlabel[4],font=font,fill=WHITE)
        draw.text((width/2 +24,28),potlabel[5],font=font,fill=WHITE)
        draw.text((width/2 +24,39),potlabel[6],font=font,fill=WHITE)
        draw.text((width/2 +24,50),potlabel[7],font=font,fill=WHITE)
        for p in range(4):
          graphics.slider(draw,p,potlabel[p],sliders[p]/255)
        for i in range(4):
          if i == 1:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=1)
          else:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=0)
      await asyncio.sleep(0.04)
      
    elif sel_page == VIEW_ADSR:
      with canvas(device) as draw:
        graphics.title(draw,'ADSR')
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        graphics.draw_adsr(draw,adsr)
        for i in range(4):
          if i == 2:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=1)
          else:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)
    elif sel_page == VIEW_TAB :
      with canvas(device) as draw:
        graphics.title(draw,'WAVEFORM')
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        graphics.wave_display_line(draw,waveform)
        for i in range(4):
          if i == 3:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=1)
          else:
            draw.rectangle((width-7, i*10+20, width-3, i*10+24), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)
    #elif sel_page == VIEW_WAVE :
    #  with canvas(device) as draw:
    #    graphics.title(draw,'WAVEFORM 2')
    #    graphics.wave_display_2(draw,waveform,wavebar)
    #  await asyncio.sleep(0.04)
    
    elif sel_page == CV_SCREEN :
      with canvas(device) as draw:
        graphics.title(draw,'CV & GATE')
        cv_gate=cv+gate
        print(cv_gate)
        for i in range(2):
          draw.rectangle(((i+2)*30+10,25,(i+2)*30+25,40), outline=WHITE, fill=not(int(gate[i])))
        
        draw.rectangle((10,25,25,40), outline=WHITE, fill=0)
        draw.rectangle((10,((cv[0]+1)/4096)*16+25,25,40), outline=WHITE, fill=1)
        
        draw.rectangle((30+10,25,30+25,40), outline=WHITE, fill=0)
        draw.rectangle((30+10,((cv[1]+1)/4096)*16+25,30+25,40), outline=WHITE, fill=1)
        
        draw.text((10,50),"cv1",font=font,fill=WHITE)
        draw.text((40,50),"cv2",font=font,fill=WHITE)
        draw.text((70,50),"gate1",font=font,fill=WHITE)
        draw.text((100,50),"gate2",font=font,fill=WHITE)
      await asyncio.sleep(0.04)
    
    elif sel_page == MIDI_SCREEN :
      with canvas(device) as draw:
        graphics.title(draw,'MIDI')
        graphics.file_display(draw,midiList,selected_midi,0)
        for i in range(len(midiSelect)):
          if midiSelect[i]==True:
            draw.rectangle((width-7, i*9+10, width-3, i*9+14), outline=WHITE, fill=1)
      await asyncio.sleep(0.04)
      
    elif sel_page == CPU_SCREEN :
      with canvas(device) as draw:
        graphics.title(draw,'CPU LOAD')
        graphics.icon_display(draw,icones.cpu,20,25,WHITE)
        draw.line((width/2+10,7,width/2+10,height),fill=WHITE)
        draw.text((width/2 +24,35),cpu,font=font,fill=WHITE)
        
      await asyncio.sleep(0.04)
      
    elif sel_page == WIFI_SCREEN :
      with canvas(device) as draw:
        graphics.title(draw,'WIFI')
        [ipadress,ssid]=cfg.getWifi()
        graphics.icon_display(draw,icones.wifi,5,23,WHITE)
        draw.line((width/2-10,7,width/2-10,height),fill=WHITE)
        draw.text((width/2,20),"ssid :",font=font,fill=WHITE)
        draw.text((width/2,30),ssid,font=font,fill=WHITE)
        draw.text((width/2,40),"ipadress :",font=font,fill=WHITE)
        draw.text((width/2,50),ipadress,font=font,fill=WHITE)
      await asyncio.sleep(0.04)
    
    elif sel_page == MAIN_MENU :
      with canvas(device) as draw:
        graphics.title(draw,'MENU')
        top_offset = 24
        prev_menu = (sel_menu-1)
        next_menu = (sel_menu+1)
        for i in range(3):
          draw.rectangle((47,top_offset-1,48+32,top_offset+32), outline=WHITE, fill=0)
          draw.rectangle((48,top_offset,48+31,top_offset+31), outline=WHITE, fill=0)
          graphics.icon_display(draw,tab_icones[sel_menu],48,top_offset,selected_color[1])
          if prev_menu >= 0:
            graphics.icon_display(draw,tab_icones[prev_menu],7,top_offset,selected_color[0])
          if next_menu <= MAX_MENU:
            graphics.icon_display(draw,tab_icones[next_menu],88,top_offset,selected_color[2])

        #for i in range(12):
        #  selected_color[i]=G3
        #  if i==sel_menu:
        #    selected_color[i]=BLACK
        #graphics.icon_display(draw,icones.files,0,top_offset,selected_color[0])
        #graphics.icon_display(draw,icones.sample,32,top_offset,selected_color[1])
        #graphics.icon_display(draw,icones.slider,64,top_offset,selected_color[2])
        #graphics.icon_display(draw,icones.pot,96,top_offset,selected_color[3])
        #graphics.icon_display(draw,icones.net,0,32+top_offset,selected_color[4])
        #graphics.icon_display(draw,icones.cv,32,32+top_offset,selected_color[5])
        #graphics.icon_display(draw,icones.pulse,64,32+top_offset,selected_color[6])
        #graphics.icon_display(draw,icones.rand,96,32+top_offset,selected_color[7])
        #graphics.icon_display(draw,icones.square,0,64+top_offset,selected_color[8])
        #graphics.icon_display(draw,icones.saw,32,64+top_offset,selected_color[9])
        #graphics.icon_display(draw,icones.tri,64,64+top_offset,selected_color[10])
        #graphics.icon_display(draw,icones.env,96,64+top_offset,selected_color[11])
      await asyncio.sleep(0.04)

    elif sel_page == DRAW_SCREEN :
      if (new):
        with canvas(device) as draw:
          new=0
          if dtype=="rect":
            draw.rectangle((coor[0],coor[1],coor[2],coor[3]), fill=WHITE)
          elif dtype=="circle":
            draw.arc((coor[0],coor[1],coor[2],coor[3]),0,360, fill=WHITE)
          elif dtype=="list":
            listlen=len(coor)
            print ("len:",listlen)
            xi=0
            while(xi<listlen):
              if coor[xi]=="rect":
                draw.rectangle((coor[xi+1],coor[xi+2],coor[xi+3],coor[xi+4]), fill=WHITE)
                xi=xi+5
              elif coor[xi]=="rectb":
                draw.rectangle((coor[xi+1],coor[xi+2],coor[xi+3],coor[xi+4]), fill=None, outline=WHITE, width=1)
                xi=xi+5
              elif coor[xi]=="circle":
                draw.ellipse((coor[xi+1]-coor[xi+3],coor[xi+2]-coor[xi+3],coor[xi+1]+coor[xi+3],coor[xi+2]+coor[xi+3]) ,fill=WHITE)
                xi=xi+4
              elif coor[xi]=="arc":
                draw.arc((coor[xi+1],coor[xi+2],coor[xi+3],coor[xi+4]),0,360, fill=WHITE)
                xi=xi+5
              elif coor[xi]=="text":
                draw.text((coor[xi+1],coor[xi+2]),coor[xi+3],font=font,fill=WHITE)
                xi=xi+4
              elif coor[xi]=="point":
                draw.point((coor[xi+1],coor[xi+2]),fill=WHITE)
                xi=xi+3
              elif coor[xi]=="points":
                tot_points=coor[xi+1]
                while tot_points:
                  draw.point((coor[xi+2],coor[xi+3]),fill=WHITE)
                  xi=xi+2
                  tot_points = tot_points-1
              elif coor[xi]=="line":
                draw.line((coor[xi+1],coor[xi+2],coor[xi+3],coor[xi+4]), fill=WHITE)
                xi=xi+5
              else :
                xi=xi+1
      await asyncio.sleep(0.01)
      update=0


     # draw.rectangle((20,20,40,40), fill=None, outline=G2, width=1)

    #if ((abs((x1-x2))<rayon)&(abs((y1-y2))<rayon)): 
     # dirx1=-dirx1
     # dirx2=-dirx2

    #  draw.rectangle(device.bounding_box, outline="white", fill="black")
    
    #logo = Image.open('/home/pi/myfiles/picto/Eowave-logo.gif')
    #image = Image.new("1", (width,height))
    #draw.rectangle((1,1, 126, 62), outline=WHITE, fill=WHITE)
    #draw.rectangle(((x*50),1,((x*50)+30),30), outline=15, fill="white")
    #draw.arc((10,10,40,40),0,360, fill=WHITE)
    #draw.ellipse((20,20, 40, 40), outline="red", fill="black")
    #draw.point((x-11,y-11), fill=GREY3)
    #draw.polygon([(x, y),(x+10,y+10),(x+19,y+9)], outline="green", fill="black")
    
    
    #draw.line ((40,0,50,50),fill=WHITE)
    #for y in range(16):
    #  draw.rectangle(((y*16),50,((y*16)+16),100), fill=(y<<4,y<<4,y<<4))
    #draw.create_image(0,8, anchor=NW, image=logo)
    #draw.paste(logo, (0,20))
    #draw.text((30, 40), "eowave", font=font_b,fill=WHITE)

    #draw.

  await asyncio.sleep(0.04)

dispatcher = dispatcher.Dispatcher()
#dispatcher.map("/midi", print)
dispatcher.map("/draw", draw_fill)
dispatcher.map("/draw/circle", draw_circle)
dispatcher.map("/draw/rect", draw_rect)
dispatcher.map("/draw/update", set_update)
dispatcher.map("/mode", set_mode)
#dispatcher.map("/pots", set_mode)
dispatcher.map("/page", set_page)
dispatcher.map("/values", set_values)
dispatcher.map("/panel", set_panel)
dispatcher.map("/waveform", set_waveform)
dispatcher.map("/waveform2", set_waveform2)
dispatcher.map("/wavebar", set_wavebar)
dispatcher.map("/adsr", set_adsr)
dispatcher.map("/sliders", set_sliders)
dispatcher.map("/pots", set_pots)
dispatcher.map("/labels", set_pots_labels)
dispatcher.map("/cpu", set_cpu)
dispatcher.map("/midi", set_midi)
dispatcher.map("/cv_gate", set_cv_gate)

async def init_main():
  
  #ip="192.168.1.49" # ip de reception
  ip="127.0.0.1" # ip de reception
  port=3002 # port de reception 
  server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
  transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
  print("listen to ip: "+str(ip)+" port: "+str(port))
    
  await update_screen()  # Enter main loop of program

  transport.close()  # Clean up serve endpoint

asyncio.run(init_main())
