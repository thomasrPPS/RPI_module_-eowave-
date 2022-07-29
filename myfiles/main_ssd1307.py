from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ssd1306,sh1106,ssd1327,ssd1322_nhd
from pathlib import Path
#import board
import time
import spidev
from PIL import Image,ImageDraw, ImageFont
#import RPi.GPIO as GPIO

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24,GPIO.OUT)
GPIO.output(24,1)

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

############TYPES DE PAGE#############
SAVER_SCREEN = 324354657
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
MATRIX_SCREEN = 12
USB_LOAD = 13
DRAW_SCREEN = 14
SAMPLE = 15
#VIEW_WAVE= 8
#STATS = 10

############listes#############
actual_value=0
adsr = [0] * 8
sliders = [0] * 8 
pots = [0] * 8
old_btn =[]
waveform = [0] * 256
waveform1= [0] * 120
waveform2= [0] * 120
patchlist=["EMPTY1","EMPTY2","EMPTY3","EMPTY4","EMPTY5","EMPTY6","EMPTY7","EMPTY8","EMPTY9","EMPTY10","EMPTY11","EMPTY12","EMPTY13"] 
presetlist=["EMPTY1","EMPTY2","EMPTY3","EMPTY4","EMPTY5","EMPTY6","EMPTY7","EMPTY8","EMPTY9","EMPTY10","EMPTY11","EMPTY12","EMPTY13"] 
usbList=[]
midiList=[]
midiSelect=[]

potlabel=[]
btnlabel=[]
btntype=[]
btntoggle=[]
tab_icones=[icones.files,icones.pot,icones.cv,icones.midi,icones.cpu,icones.wifi]
compteurs_btn=[]

sel_page = -1
sel_menu = 0
MAX_MENU = len(tab_icones)-1

wavebar = 0
selected_patch = 0
selected_preset = 0
selected_usb = 0

save_preset = 0
selected_midi = 0

screen_mode=0
index_page=0
dsp_page=[]
dsp_title=["EMPTY1","EMPTY2","EMPTY3","EMPTY4","EMPTY5","EMPTY6","EMPTY7","EMPTY8","EMPTY9","EMPTY10","EMPTY11","EMPTY12","EMPTY13"] 


############COLOUR#############
BLACK="black"
WHITE="white"
GREY=(60,60,60)
GREY3=(40,40,40)
GREY2=(30,30,30)
G1=(20,20,20)
G2=(30,30,30)
G3=(40,40,40)


update=0
new = 0
coor=(0,0,0,0)
dtype="rect"
anim = 0
selected_color =[G3] * 12
width =128
height =64
FONTSIZE = 12
list_offset=0
cv=[0,0]
gate=[0,0]
cpu="... %"
ssid=""
ipadress=""
draw_page=0
cursor = 0
compt = 20
waveform_tgl=["sine","lramp","rramp","tri","sqre","llramp","lrramp","lbent","ltri","lsqre"]
list_multi_tgl=[]
font_b = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE+10)
#font = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE)
font = ImageFont.load("/home/pi/myfiles/fonts/bitocra7.pil")
#font_s = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE-1)
#font_s2 = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE-2)

#img_1 = Image.open('/home/pi/myfiles/fonts/c.gif')

for x in range(127):
    waveform[x]=x/2

# rev.1 users set port=0
 #substitute spi(device=0, port=0) # below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
#serial = spi(device=0, port=0,gpio_DC=23) 
serial = spi(device=0, port=0,gpio_DC=25) 

#serial = i2c(port=1, address=0x3C)
# substitute ssd1331(...) or sh1106(...) below if using that device
#device = ssd1306(serial)
#device = sh1106(serial)
device = ssd1322_nhd(serial, width=128, height=64, rotate = 2)

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
  global selected_usb
  global save_preset
  global selected_midi
  global patchlist
  global presetlist
  global usbList
  global sel_menu

  global screen_mode
  global sel_page
  global index_page

  print("selpage : %s",sel_page)
  print("screen_mode : %s",screen_mode)
  print("index_page : %s",index_page)

  patch_len= len(patchlist)
  preset_len= len(presetlist)  

  if (screen_mode== 0):
    if (sel_page==LIST_SCREEN):
      if args[0]=="UP" and selected_patch < patch_len-1:
        selected_patch=selected_patch+1

      elif args[0]=="DOWN" and selected_patch >0:
        selected_patch=selected_patch-1
      
      elif args[0]=="ENTER":
        client.send_message("/load", patchlist[selected_patch])
        presetlist=cfg.readPresetList(patchlist[selected_patch])
        client.send_message("/preset", presetlist[selected_preset])
        screen_mode= 1
        index_page = 0
      elif args[0]=="ESC":
        sel_page= 0
        screen_mode= 0
    
    elif (sel_page==LIST_PRESET):
      if args[0]=="UP":
        selected_preset=selected_preset+1
        if selected_preset >= preset_len: selected_preset=preset_len-1

      elif args[0]=="DOWN":
        selected_preset=selected_preset-1
        if selected_preset <0: selected_preset=0
      
      elif args[0]=="ENTER":
        client.send_message("/preset", presetlist[selected_preset])
        #client.send_message("/menu", 0)
        screen_mode= 1
        sel_page=dsp_page[index_page]
      elif args[0]=="ENTER_HOLD":
        sel_page= SAVE_PRESET
        client.send_message("/menu", 11)
      elif args[0]=="ESC":
        screen_mode= 1
        sel_page=dsp_page[index_page]
    
    elif (sel_page==SAVE_PRESET):
      if args[0]=="UP":
        save_preset=save_preset+1
        if save_preset >= preset_len: save_preset=preset_len-1

      elif args[0]=="DOWN":
        save_preset=save_preset-1
        if save_preset <0: save_preset=0
      
      elif args[0]=="ENTER":
        client.send_message("/preset_save", presetlist[save_preset])
        client.send_message("/menu", 0)
        screen_mode= 1
        sel_page=dsp_page[index_page]
      elif args[0]=="ESC":
        screen_mode= 1
        sel_page=dsp_page[index_page]
        
    elif (sel_page==MAIN_MENU):
      if args[0]=="UP":
        sel_menu=sel_menu+1
        if sel_menu >= MAX_MENU: sel_menu= MAX_MENU
      elif args[0]=="DOWN":
        sel_menu=sel_menu-1
        if sel_menu <0: sel_menu=0
      elif args[0]=="ENTER":
        if sel_menu == 0:
          patchlist=cfg.readPatchList(0)
          sel_page = 1
        elif sel_menu == 1:
          #if dsp_page:
          screen_mode= 1
          sel_page=dsp_page[index_page]
        elif sel_menu == 2:
          sel_page =6
          client.send_message("/param",sel_page)
        elif sel_menu == 3:
          sel_page =7
          client.send_message("/param",sel_page)
        elif sel_menu == 4:
          sel_page =8
          client.send_message("/param",sel_page)
        elif sel_menu == 5:
          sel_page =9
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

  elif (screen_mode== 1):
    print("enter screenmode + index = ",index_page)
    if args[0]=="ESC":
      screen_mode = 0
      sel_page=1
    elif args[0]=="DOWN":
      if index_page>0:
        index_page-=1
        sel_page=dsp_page[index_page]
        client.send_message("/menu", index_page)
    elif args[0]=="UP":
      if index_page<len(dsp_page)-1:
        index_page+=1
        sel_page=dsp_page[index_page]
        client.send_message("/menu", index_page)
    elif args[0]=="ENTER":
      presetlist=cfg.readPresetList(patchlist[selected_patch])
      screen_mode= 0
      sel_page=LIST_PRESET
      client.send_message("/param",sel_page)
  
  elif (sel_page==USB_LOAD):
    if args[0]=="ESC":
      sel_menu=9
      sel_page=0
    elif args[0]=="UP":
      selected_usb=selected_usb+1
      if selected_usb >= len(usbList): selected_usb=len(usbList)-1

    elif args[0]=="DOWN":
      selected_usb=selected_usb-1
      if selected_usb <0: selected_usb=0
    elif args[0]=="ENTER":
      client.send_message("/load_USB", usbList[selected_usb])
      presetlist=cfg.readPresetList(patchlist[selected_patch])
      sel_menu= POT_SCREEN
      sel_page= POT_SCREEN


def set_display_page(unused_addr, *args):
  global dsp_page
  global sel_page
  global potlabel
  global btnlabel
  global btntype
  global btntoggle
  global screen_mode
  global old_btn
  global compteurs_btn

  old_btn = [0] * len(args)*4
  compteurs_btn = [0] * len(args)*4

  dsp_page = []
  for i in range(len(args)):
    if args[i] == "POT":
      dsp_page.append(2)
    elif args[i] == "SLIDER":
      dsp_page.append(3)
    elif args[i] == "DRAW":
      dsp_page.append(14)
    elif args[i] == "ADSR":
      dsp_page.append(4)
    elif args[i] == "SAMPLE":
      dsp_page.append(15)
  #attribuer le bon nombre de labels aux textfields
  potlabel = ["empty"] * len(args)*4
  btnlabel = ["empty"] * len(args)*4
  btntype  = ["btn"]   * len(args)*4
  btntoggle  = [False]   * len(args)*4
  
  dsp_title = [0] * len(args)
  screen_mode = 1
  sel_page=dsp_page[index_page]  
  client.send_message("/menu", index_page)
  print(dsp_page)

def set_display_title(unused_addr, *args):
  global dsp_title
  lengg= len(args)
  dsp_title=args
  for i in range(len(dsp_page)-lengg):
    dsp_title=dsp_title+ ("EMPTY PAGE :)",)
  
def set_mode(unused_addr, *args):
  global screen_mode
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

def set_sliders(unused_addr, *args):
  global sliders
  sliders=args
 
def set_pots(unused_addr, *args):
  global pots
  global index_page
  pots=args
  for i in range(4):
    if old_btn[index_page*4+i] != pots[4+i]:
      old_btn[index_page*4+i] = pots[4+i]
      compteurs_btn[index_page*4+i] = 10

def set_update(unused_addr, *args):
  global update
  update=1
  #("update : ",update)

def set_page(unused_addr, *args):
  global sel_page
  # (args)
  sel_page=int(args[0])
  
def set_draw_page(unused_addr, *args):
  global draw_page
  draw_page = int(args[0])

def set_waveform(unused_addr, *args): #must be 128
  global waveform
  print(args)
  for i in range(120):
    waveform1[i]=args[i]
  for i in range(120):
    waveform2[i]=args[i+128]

def set_waveform2(unused_addr, *args): #must be 128
  global waveform
  for i in range(256):
    waveform[i]=args[i]

def set_wavebar(unused_addr, *args): #must be 128
  global wavebar
  wavebar=args[0]

def set_values(unused_addr, *args):
  global actual_value
  actual_value=int(args[0])
  
def set_pots_labels(unused_addr, *args):
  global potlabel
  temp=0
  for temp in range(len(dsp_page)*4):
    if isinstance(args, str) and temp < len(args):
      potlabel[temp]=args[temp]
    elif temp<len(args):
      potlabel[temp]=str(args[temp])
    else:
      potlabel[temp]="empty"
      
def set_btn_labels(unused_addr, *args):
  global btnlabel
  temp=0
  for temp in range(len(dsp_page)*4):
    if isinstance(args, str) and temp < len(args):
      btnlabel[temp]=args[temp]
    elif temp<len(args):
      btnlabel[temp]=str(args[temp])
    else:
      btnlabel[temp]="empty"

def set_btn_type(unused_addr, *args):
  global potlabel
  temp=0
  for temp in range(len(dsp_page)*4):
    if isinstance(args, str) and temp < len(args):
      btnlabel[temp]=args[temp]
    elif temp<len(args):
      btntype[temp]=str(args[temp])
    else:
      btntype[temp]="off"

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

def set_cursor(unused_addr, *args):
  global cursor
  cursor=args[0]

def set_list_multi_tgl(unused_addr, *args):
  global list_multi_tgl
  list_multi_tgl=args
      

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
  global draw_page
  global dsp_page
  global index_page

  global new
  global coor
  global dtype
  global wavebar
  global cursor
  
  global ssid
  global ipadress

  global compt

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
        if x2 <118:
          x2+=2
        draw.rectangle((10,40,118,30), outline=WHITE, fill=BLACK)
        draw.rectangle((10,40,x2,30), outline=WHITE, fill=WHITE)
        await asyncio.sleep(0.002)
         
    

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

    elif sel_page == POT_SCREEN:
      with canvas(device) as draw:
        graphics.title(draw,dsp_title[index_page])
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        for p in range(4):
          version = "pot"
          graphics.pot(draw,p,potlabel[p+index_page*4],pots[p]/63,version,0)
        for p in range(4):
          if pots[p+4]==1 and btntype[p+index_page*4]=="btn":
            graphics.pot(draw,p,btnlabel[p+index_page*4],pots[p+4]/63,btntype[p+index_page*4],0)
          elif btntype[p+index_page*4]=="tgl":
            graphics.pot(draw,p,btnlabel[p+index_page*4],pots[p+4]/63,btntype[p+index_page*4],pots[p+4])
          elif btntype[p+index_page*4]=="multi":
            graphics.pot(draw,p,btnlabel[p+index_page*4],pots[p+4]/63,btntype[p+index_page*4],int(pots[p+4]))
          elif btntype[p+index_page*4]=="multi_w":
            graphics.pot(draw,p,btnlabel[p+index_page*4],pots[p+4]/63,btntype[p+index_page*4],int(pots[p+4]))
        
        for p in range(4):
          if btntype[p+index_page*4]=="multi":
            if compteurs_btn[index_page*4+p] >0:
              graphics.animWave(draw,p,int(pots[p+4]),list_multi_tgl)
              compteurs_btn[index_page*4+p]=compteurs_btn[index_page*4+p]-1
          elif btntype[p+index_page*4]=="multi_w":
            if compteurs_btn[index_page*4+p] >0:
              graphics.animWave(draw,p,int(pots[p+4]),waveform_tgl)
              compteurs_btn[index_page*4+p]=compteurs_btn[index_page*4+p]-1
        
        

        for i in range(len(dsp_page)):
          if i == index_page: 
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=WHITE)
          else:
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)

    elif sel_page == SLIDER_SCREEN:
      with canvas(device) as draw:
        graphics.title(draw,dsp_title[index_page])
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        draw.line((width/2+20,7,width/2+20,height),fill=WHITE)
        draw.text((width/2 +24,17),potlabel[0+index_page*4],font=font,fill=WHITE)
        draw.text((width/2 +24,28),potlabel[1+index_page*4],font=font,fill=WHITE)
        draw.text((width/2 +24,39),potlabel[2+index_page*4],font=font,fill=WHITE)
        draw.text((width/2 +24,50),potlabel[3+index_page*4],font=font,fill=WHITE)
        for p in range(4):
          version = "pot"
          graphics.slider(draw,p,potlabel[p+index_page*4],pots[p]/255,version,0)
        for p in range(4):
          if pots[p+4]==1 and btntype[p+index_page*4]=="btn":
            graphics.slider(draw,p,btnlabel[p+index_page*4],pots[p]/255,btntype[p+index_page*4],0)
          elif btntype[p+index_page*4]=="tgl":
            graphics.slider(draw,p,btnlabel[p+index_page*4],pots[p]/255,btntype[p+index_page*4],pots[p+4])
          elif btntype[p+index_page*4]=="multi":
            graphics.slider(draw,p,btnlabel[p+index_page*4],pots[p]/255,btntype[p+index_page*4],int(pots[p+4]))

        for i in range(len(dsp_page)):
          if i == index_page: 
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=WHITE)
          else:
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=0)
      await asyncio.sleep(0.04)

    elif sel_page == SAMPLE:
      with canvas(device) as draw:
        graphics.title(draw,dsp_title[index_page])
        draw.text((width-42,10),"speed:x",font=font,fill=WHITE)
        draw.text((width-13,10),str(int(pots[2]/48)),font=font,fill=WHITE)
        draw.text((width-42,16),"volum:",font=font,fill=WHITE)
        draw.text((width-17,16),str(pots[3]/256)[1:3],font=font,fill=WHITE)
        #draw.rectangle((5,15,123,60),outline=WHITE, fill=BLACK,width=1)
        print(waveform1,waveform2)
        graphics.wave_display_2(draw,waveform1,waveform2)

        #draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        
        graphics.cursor(draw,pots[0],pots[1],cursor)

        for p in range(4):
          if btntype[p+index_page*4]=="multi":
            if compteurs_btn[index_page*4+p] >0:
              graphics.animWave(draw,1,int(pots[p+4]),list_multi_tgl)
              compteurs_btn[index_page*4+p]=compteurs_btn[index_page*4+p]-1

        for i in range(len(dsp_page)):
          if i == index_page: 
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=WHITE)
          else:
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)
      
      
    elif sel_page == VIEW_ADSR:
      with canvas(device) as draw:
        graphics.title(draw,dsp_title[index_page])
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        graphics.draw_adsr(draw,pots)
        
        for i in range(len(dsp_page)):
          if i == index_page: 
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=WHITE)
          else:
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=0)

      await asyncio.sleep(0.04)

    elif sel_page == VIEW_TAB :
      with canvas(device) as draw:
        graphics.title(draw,'WAVEFORM')
        draw.text((width-15,0),str(actual_value),font=font,fill=WHITE)
        graphics.wave_display_line(draw,waveform)
        

        for i in range(len(dsp_page)):
          if i == index_page: 
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=WHITE)
          else:
            draw.rectangle((width-7, i*((height-10)/len(dsp_page))+15, width-3, i*((height-10)/len(dsp_page))+19), outline=WHITE, fill=0)

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
        for i in range(2):
          if not(int(gate[i])) == 0 :
            fill_c = BLACK
          else : 
            fill_c = WHITE
          draw.rectangle(((i+2)*30+10,25,(i+2)*30+25,40), outline=WHITE, fill=fill_c)
        
        draw.rectangle((10,25,25,40), outline=WHITE, fill=BLACK)
        draw.rectangle((10,((cv[0]+1)/4096)*16+25,25,40), outline=WHITE, fill=WHITE)
        
        draw.rectangle((30+10,25,30+25,40), outline=WHITE, fill=BLACK)
        draw.rectangle((30+10,((cv[1]+1)/4096)*16+25,30+25,40), outline=WHITE, fill=WHITE)
        
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
            draw.rectangle((width-7, i*9+10, width-3, i*9+14), outline=WHITE, fill=WHITE)
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

    elif sel_page == USB_LOAD :
      with canvas(device) as draw:
        graphics.title(draw,'USB LOAD')
        graphics.file_display(draw,usbList,selected_usb,0)
      await asyncio.sleep(0.04)
    
    elif sel_page == MATRIX_SCREEN :
      with canvas(device) as draw:
        x=-20
        y=5
        graphics.title(draw,'MATRIX')
        draw.rectangle((x+50,y+15,x+80,y+45),outline=WHITE, fill =0)
        draw.rectangle((x+30,y+25,x+60,y+55),outline=WHITE, fill =0)
        draw.line((x+30,y+25,x+50,y+15),fill=WHITE)
        draw.line((x+60,y+55,x+80,y+45),fill=WHITE)
        draw.line((x+60,y+25,x+80,y+15),fill=WHITE)
        draw.line((x+30,y+55,x+50,y+45),fill=WHITE)
        draw.line((x+50,y+15,x+50,y+45),fill=WHITE)
        draw.line((x+50,y+45,x+80,y+45),fill=WHITE)
        
        #draw.rectangle((x+30+X*30,y+25+Y*30,x+60+Z*30,y+55+Y*30),outline=WHITE, fill =0)
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
          draw.rectangle((48,top_offset+1,48+30,top_offset+30), outline=WHITE, fill=0)
          graphics.icon_display(draw,tab_icones[sel_menu],48,top_offset,selected_color[1])
          if prev_menu >= 0:
            graphics.icon_display(draw,tab_icones[prev_menu],7,top_offset,selected_color[0])
          if next_menu <= MAX_MENU:
            graphics.icon_display(draw,tab_icones[next_menu],88,top_offset,selected_color[2])

      await asyncio.sleep(0.04)

    elif sel_page == DRAW_SCREEN :
      if (new):
        with canvas(device) as draw:
          graphics.title(draw,'draw')

          for i in range(len(dsp_page)):
            if i == index_page: 
              draw.rectangle((width-7, i*((height-10)/len(dsp_page))+10, width-3, i*((height-10)/len(dsp_page))+14), outline=WHITE, fill=WHITE)
            else:
              draw.rectangle((width-7, i*((height-10)/len(dsp_page))+10, width-3, i*((height-10)/len(dsp_page))+14), outline=WHITE, fill=0)

          new=0
          if dtype=="rect":
            draw.rectangle((coor[0],coor[1],coor[2],coor[3]), fill=WHITE)
          elif dtype=="circle":
            draw.arc((coor[0],coor[1],coor[2],coor[3]),0,360, fill=WHITE)
          elif dtype=="list":
            listlen=len(coor)
            xi=0
            while(xi<listlen):
              if coor[xi]=="rect":
                draw.rectangle((coor[xi+1],coor[xi+2],coor[xi+3],coor[xi+4]), fill=WHITE)
                xi=xi+5
              elif coor[xi]=="sea_back":
                graphics.sea_back(draw,coor[xi+1],coor[xi+2],coor[xi+3])
                xi=xi+4
              elif coor[xi]=="round_alea":
                graphics.round_alea(draw,coor[xi+1],coor[xi+2],coor[xi+3])
                xi=xi+4
              elif coor[xi]=="city_run":
                graphics.city_run(draw,coor[xi+1])
                xi=xi+2
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
      await asyncio.sleep(0.02)
      update=0

  await asyncio.sleep(0.04)

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/draw", draw_fill)
dispatcher.map("/draw/circle", draw_circle)
dispatcher.map("/draw/rect", draw_rect)
dispatcher.map("/draw/update", set_update)
dispatcher.map("/draw_page", set_draw_page)
dispatcher.map("/display_page", set_display_page)
dispatcher.map("/display_title", set_display_title)
dispatcher.map("/list_multi_tgl", set_list_multi_tgl)
dispatcher.map("/mode", set_mode)
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
dispatcher.map("/labels_btn", set_btn_labels)
dispatcher.map("/type_btn", set_btn_type)
dispatcher.map("/cpu", set_cpu)
dispatcher.map("/midi", set_midi)
dispatcher.map("/cv_gate", set_cv_gate)
dispatcher.map("/cursor", set_cursor)

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
dispatcher.map("/labels_btn", set_btn_labels)
