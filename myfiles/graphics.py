
from PIL import Image,ImageDraw, ImageFont
import math

BLACK="black"
WHITE="white"
G2=WHITE
G10=WHITE
#G2=(30,30,30)
#G10=(100,100,100)
FONTSIZE = 12


#font = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE)
font = ImageFont.load("/home/pi/myfiles/fonts/bitocra7.pil")
fontsize = 9
width = 128
height = 64
MAX_LINES = 5

def title(draw,title):
    global height
    global width
    draw.line ((0,7,width,7),fill=WHITE)
    draw.text((2,0),title,font=font,fill=WHITE)

def wave_display(draw,tabx):
    global height
    global width
    mid =height/2 + 6
    for x in range(width):
        draw.point((x,mid-tabx[x]*30),fill=WHITE)

def wave_display_line(draw,tabx):
    global height
    global width
    mid =height/2 + 6
    x=0
    draw.line((0,32,0,mid-tabx[x]),fill=WHITE)
    for x in range(width-12):
        draw.line((x,mid-tabx[x]*30,x+1,mid-tabx[x+1]),fill=WHITE)

def wave_display_2(draw,tabx,wavebar):
    global height
    global width
    mid =height/2
    if wavebar>0:
        draw.line((wavebar*width,10,wavebar*width,height),fill=WHITE)
    for x in range(0,width*2,2):
        draw.line((x/2,mid-tabx[x]*32,x/2,mid-tabx[x+1]*32),fill=WHITE)

def draw_adsr(draw,adsr):
  max_x=108
  max_y=60
  tot=adsr[0]+adsr[1]+adsr[3]+20;
  a=(adsr[0]*max_x)/tot;
  d=((adsr[1]*max_x)/tot)+a;
  s=((20*max_x)/tot)+d;
  r=max_x-2;
  sus_level=max_y-adsr[2]/7.5

  #draw.rectangle((0, 10, 122, 122), outline=0, fill=0)

  #draw.line((0,127,a,26),fill=WHITE)
  #draw.line((a,11,d,sus_level),fill=WHITE)
  #draw.line((d,sus_level,s,sus_level),fill=WHITE)
  #draw.line((s,sus_level,121,127),fill=WHITE) 
  draw.line((0,63,a,26,d,sus_level,s,sus_level,110,60),fill=WHITE)
  draw.rectangle((a-2,24,a+2,28), outline=WHITE, fill=0)
  draw.rectangle((d-2,sus_level-2,d+2,sus_level+2), outline=WHITE, fill=0)
  draw.rectangle((s-2,sus_level-2,s+2,sus_level+2), outline=WHITE, fill=0)


def pot128(draw,pos,label,value): # version ecran 128 x 128 
    global font
    global height
    global width
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= ((value)*0.8)+0.7
    posx = ((pos % 3)*43)+6
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    
    posy =(int(pos / 3)*52)+20
    draw.arc((posx,posy,posx+31,posy+31),0,360, fill=WHITE)
    draw.text((posx+15-sl,posy+31),label,font=font,fill=WHITE)
    x_t=(posx+15)+(15*math.cos(math.pi*value))
    y_t=(posy+15)+(15*math.sin(math.pi*value))
    draw.line ((posx+15,posy+15,x_t,y_t),fill=WHITE)

def pot(draw,pos,label,value): # version ecran 128 x 128 
    global font
    global height
    global width
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= ((value)*0.4)+0.7
    posx = ((pos % 4)*32)+3
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    
    posy =(int(pos / 4)*30)+28
    draw.arc((posx,posy,posx+17,posy+17),0,360, fill=WHITE)
    draw.text((posx+9-sl,posy+17),label,font=font,fill=WHITE)
    x_t=(posx+9)+(9*math.cos(math.pi*value))
    y_t=(posy+9)+(9*math.sin(math.pi*value))
    draw.line ((posx+9,posy+9,x_t,y_t),fill=WHITE)
    

def slider128(draw,pos,label,value): # version ecran 128 x 128 
    global font
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= 123-value*96
    pos = pos*16+4
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    
    draw.line ((pos,20,pos,127),fill=WHITE)
    draw.ellipse((pos-4,value-4,pos+4,value+4),outline=WHITE, fill=BLACK,width=1)
    #draw.text((pos-sl,101),str(value)[0:2],font=font,fill=WHITE)

def slider(draw,pos,label,value): # version ecran 128 x 63 
    global font
    global height
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= height-value*(height-14) -3
    pos = pos*20+4
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    
    draw.line ((pos,10,pos,127),fill=WHITE)
    draw.ellipse((pos-2,value-2,pos+2,value+2),outline=WHITE, fill=BLACK,width=1)
    #draw.text((pos-sl,101),str(value)[0:2],font=font,fill=WHITE)

def file_display(draw,patch_list,selected,list_offset):
    global width,height,fontsize
    global MAX_LINES 
    max_files = len(patch_list)
    if selected>=MAX_LINES:
        #(list_offset+3):
        list_offset=selected-MAX_LINES
    else :
        list_offset = 0
    for i in range(MAX_LINES+1):
        if (i+list_offset) == selected and i+list_offset <max_files :
            draw.rectangle((0, ((i*fontsize)+fontsize-1), width-10, ((i*fontsize)+(fontsize*2)-2)), fill=G2)
            draw.text((2,(i*fontsize)+fontsize),'>'+patch_list[i+list_offset].upper(),font=font,fill=BLACK)
        elif (i+list_offset <max_files) :
            draw.text((2,(i*fontsize)+fontsize),'>'+patch_list[i+list_offset].upper(),font=font,fill=WHITE)

def icon_display(draw,im,x,y,color):  #32x32
    if color == BLACK:
        draw.rectangle((x,y,x+31,y+31), outline=WHITE, fill=0)
    for i in range(len(im)):
        line = im[i]
        for j in range(8):
            if line & 0x80:
                draw.point((((i%4)<<3)+j+x,(i>>2)+y),WHITE)
            line = line << 1
