from PIL import Image,ImageDraw, ImageFont
import math
import numpy as np

BLACK="black"
WHITE="white"
#G2=WHITE
#G10=WHITE
G1=(10,10,10)
G2=(20,20,20)
G3=(30,30,30)
G4=(40,40,40)
G5=(50,50,50)
G6=(60,60,60)
G7=(70,70,70)
G8=(80,80,80)
G9=(90,90,90)
G10=(100,100,100)
G20=(200,200,200)
FONTSIZE = 14

waveform_tgl=["sine","lramp","rramp","tri","sqre","llramp","lrramp","lbent","ltri","lsqre"]
multi_btn_count=0

#font = ImageFont.truetype("/home/pi/myfiles/fonts/VT323-Regular.ttf", FONTSIZE)
font = ImageFont.load("/home/pi/myfiles/fonts/bitocra7.pil")
fontsize = 9
width = 128
height = 64
MAX_LINES = 5

compt= 1

def title(draw,title):
    global height
    global width
    draw.text((2,0),title,font=font,fill=WHITE)
    draw.line ((0,7,width-10,7),fill=WHITE)

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

def wave_display_2(draw,tabup,tabdown):
    global height
    global width
    mid =height/2 +5
    for x in range(0,110,1):
        draw.line((x+11,mid-tabup[x]*20,x+11,mid-tabdown[x]*20),fill=G3)

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

def pot(draw,pos,label,value,version,tgl): # version ecran 128 x 128 
    global font
    global height
    global width
    global waveform_tgl
    global multi_btn_count
    global compt
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= ((value)*0.4)+0.7
    posx = ((pos % 4)*30)+3
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    
    posy =(int(pos / 4)*30)+30
    if version == "pot":
        draw.arc((posx,posy,posx+17,posy+17),0,360, fill=WHITE)
        draw.text((posx+9-sl,posy+20),label,font=font,fill=WHITE)
        x_t=(posx+9)+(9*math.cos(math.pi*value))
        y_t=(posy+9)+(9*math.sin(math.pi*value))
        draw.line ((posx+9,posy+9,x_t,y_t),fill=WHITE)
    if version == "btn":
        draw.arc((posx-2,posy-2,posx+19,posy+19),0,360, fill=WHITE)
        draw.text((posx+9-sl,posy+28),label,font=font,fill=WHITE)
    if version == "tgl":
        draw.ellipse((posx+10,posy-15,posx+22,posy-3), outline=WHITE, fill=BLACK)
        if tgl== 1:
            draw.ellipse((posx+10,posy-15,posx+22,posy-3), outline=WHITE, fill=WHITE)
            draw.text((posx+9-sl,posy+27),label,font=font,fill=WHITE)
    if version == "multi":
        draw.arc((posx+10,posy-15,posx+22,posy-3),0,360, fill=WHITE)
        draw.text((posx+15,posy-12),str(tgl),font=font,fill=WHITE)
        draw.text((posx+9-sl,posy+27),label,font=font,fill=WHITE)
    if version == "multi_w":
        draw.arc((posx+10,posy-15,posx+22,posy-3),0,360, fill=WHITE)
        draw.text((posx+13,posy-12),str(waveform_tgl[tgl][:2]),font=font,fill=WHITE)
        draw.text((posx+9-sl,posy+27),waveform_tgl[tgl],font=font,fill=WHITE)
            
        
    

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

def slider(draw,pos,label,value,version,tgl): # version ecran 128 x 63 
    global font
    global height
    nlabel=str(value)
    nlabel=nlabel[0:4]
    value= height-value*(height-14) -3
    pos = pos*20+4
    sl_len= font.getsize(label)
    sl =sl_len[0]/2
    draw.line ((pos,10,pos,127),fill=WHITE)
    if version == "pot":
        draw.ellipse((pos-2,value-2,pos+2,value+2),outline=WHITE, fill=BLACK,width=1)
    #draw.text((pos-sl,101),str(value)[0:2],font=font,fill=WHITE)
    if version == "btn":
        draw.text((pos+5,value-8),label,font=font,fill=WHITE)
        draw.ellipse((pos-3,value-3,pos+3,value+3),outline=WHITE, fill=WHITE,width=1)
    if version == "tgl":
        draw.rectangle((pos-2,value-2,pos+2,value+2),outline=WHITE, fill=BLACK,width=1)
        if tgl== 1:
            draw.text((pos+5,value-10),label,font=font,fill=WHITE)
            draw.rectangle((pos-2,value-2,pos+2,value+2),outline=WHITE, fill=WHITE,width=1)
    if version == "multi":
        draw.rectangle((pos-2,value-2,pos+2,value+2),outline=WHITE, fill=BLACK,width=1)
        draw.text((pos+5,value-10),label,font=font,fill=WHITE)
        draw.text((pos+5,value-3),str(tgl),font=font,fill=WHITE)

        

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
            draw.rectangle((0, ((i*fontsize)+fontsize-1), width-10, ((i*fontsize)+(fontsize*2)-2)), fill=(92,92,92))
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
            
def sea_back(draw,birds,waves,cloud):#step = 20 max
    draw.line((20,15+(birds%10),33,25),fill=WHITE)
    draw.line((35,25,40,15+(birds%10)),fill=WHITE)
    draw.line((47,40,55,27+(birds%10)),fill=WHITE)
    draw.line((42,27+(birds%10),47,40),fill=WHITE)
    draw.line((57,30,65,17+(birds%10)),fill=WHITE)
    draw.line((50,17+(birds%10),57,30),fill=WHITE)
    draw.line((5,47+(waves%5),56,47+(waves%5)),fill=WHITE)
    draw.line((22,56+(waves%5),67,56+(waves%5)),fill=WHITE)
    draw.line((63,52+(waves%5),97,52+(waves%5)),fill=WHITE)
    draw.line((72,50+(waves%5),115,50+(waves%5)),fill=WHITE)
    draw.arc((70+(cloud%15),20,90+(cloud%15),40),0,300, fill=WHITE)
    draw.arc((85+(cloud%15),15,95+(cloud%15),25),110,360, fill=WHITE)
    draw.arc((90+(cloud%15),25,105+(cloud%15),40),340,180, fill=WHITE)
    draw.arc((95+(cloud%15),17,110+(cloud%15),32),180,50, fill=WHITE)
    
def round_alea(draw,speed,nbr,size):
    for i in range(int(nbr)%30):
        x=np.random.rand(1)*(128-int(size))
        y=np.random.rand()*(45-int(size))+15
        draw.arc((x,y,x+(size%15),y+(size%15)),0,360, fill=WHITE)
    
def city_run(draw,speed):
    tab=([[110,15,119,64],[93,13,97,64],[86,22,90,64],[82,29,86,64],[66,32,70,64],[61,16,66,64],[63,9,64,64],[55,23,61,64],[27,32,55,33],[21,21,28,64],[12,16,18,64],[1,22,8,64]])
    
    for i in range(len(tab)):
        x1=(tab[i][0]+speed)%128
        x2 =(tab[i][2]+speed)%128
        fenx=np.random.rand(1)*128
        feny=np.random.rand(1)*64
        if x1 >= (tab[i][0]+speed):
            x2 =(tab[i][2]+speed)
        
        draw.rectangle((x1,tab[i][1],x2,tab[i][3]), outline=WHITE, fill=WHITE)
        draw.rectangle((fenx,feny,fenx+1,feny+1), outline=BLACK, fill=BLACK)

def cursor(draw,startR,stopR,cursorR):
    start = (startR*0.9 )/2.2 + 10
    stop = (stopR*0.9 )/2.2 + 10
    cursor = ((cursorR *0.9 )/2.2)*2 + 9
    
    draw.rectangle((start,24,start,50),outline=WHITE, fill=BLACK,width=1)
    draw.rectangle((start-2,20,start+2,24),outline=WHITE, fill=BLACK,width=1)
    draw.rectangle((stop,24,stop,50),outline=WHITE, fill=BLACK,width=1)
    draw.rectangle((stop-2,20,stop+2,24),outline=WHITE, fill=BLACK,width=1)
    
    draw.rectangle((cursor,25,cursor+2,50),outline=BLACK, fill=G20,width=1)

def animWave(draw,pos,tgl,waveform_tgl):
    draw.rounded_rectangle((20+pos*30,15,40+pos*30,23),4,outline=G5, fill=BLACK)
    draw.text((23+pos*30,16),str(waveform_tgl[(tgl-2)%(len(waveform_tgl))])[:4],font=font,fill=G5)
    
    draw.rounded_rectangle((22+pos*30,25,42+pos*30,33),4,outline=G10, fill=BLACK)
    draw.text((25+pos*30,26),str(waveform_tgl[(tgl-1)%(len(waveform_tgl))])[:4],font=font,fill=G10)
    
    draw.rounded_rectangle((23+pos*30,34,45+pos*30,44),4,outline=WHITE, fill=BLACK,width=2)
    draw.text((27+pos*30,36),str(waveform_tgl[(tgl)])[:4],font=font,fill=WHITE)
    draw.rounded_rectangle((22+pos*30,45,42+pos*30,53),4,outline=G10, fill=BLACK)
    draw.text((25+pos*30,46),str(waveform_tgl[(tgl+1)%(len(waveform_tgl))])[:4],font=font,fill=G10)
    draw.rounded_rectangle((20+pos*30,55,40+pos*30,63),4,outline=G5, fill=BLACK)
    draw.text((23+pos*30,56),str(waveform_tgl[(tgl+2)%(len(waveform_tgl))])[:4],font=font,fill=G5)
    
    
