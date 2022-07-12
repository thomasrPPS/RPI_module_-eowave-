import os
import serial
import struct
import time


#________________________CONSTANTES______________________________#


device = 1 #0 pour la carte sd et 1 pour la clef usb

usbPath = "/media/usb/"
sdPath = "/home/pi/myfiles/pd/"

midiList=[]

#____________________SYSTEM____________________#

def readPatchList(vol):
	global patch_list_usb, patch_list_sd
	if vol==1:
		patch_list_usb = sorted(os.listdir(usbPath)) #list of atmnt folder in the previous folder
	
		i = 0
		while(i<len(patch_list_usb)):
			if patch_list_usb[i]!=patch_list_usb[i].replace('.',''):
				del patch_list_usb[i]
				i -= 1
			i += 1
	else:
		patch_list_sd = sorted(os.listdir(sdPath)) #list of atmnt folder in the previous folder
		i = 0
		while(i<len(patch_list_sd)):
			if patch_list_sd[i]!=patch_list_sd[i].replace('.',''):
				del patch_list_sd[i]
				i -= 1
			i += 1
	return patch_list_sd

def readPresetList(selected_patch):
	global patch_list_sd
	preset_list_sd = sorted(os.listdir(sdPath+"/"+selected_patch)) #list of atmnt folder in the previous folder
	i = 0
	while(i<len(preset_list_sd)):
		if preset_list_sd[i]==preset_list_sd[i].replace('.txt','') or preset_list_sd[i]==preset_list_sd[i].replace('preset',''):
			del preset_list_sd[i]
			i -= 1
		i += 1
	return preset_list_sd


def start_pd():
	#os.system('sudo pd -nogui -alsamidi -mididev 1 /home/pi/myfiles/main_patch_2006.pd &')
	os.system('sudo pd -alsamidi -mididev 1 /home/pi/myfiles/main_patch_2406.pd &')
	time.sleep(2)
	os.system("aconnect 20:1 128:0")
	os.system("aconnect 128:1 20:0")
	
#____________________MIDI____________________#

def getMidiList():
	global midiList
	midiList=[]
	temp= os.popen('aconnect -l').read()
	length = len(temp)
	temp= str(temp[6:length])
	temp=temp[temp.find("client")-2:length]
	print(temp)
	if temp != "":
		while (temp.find("client") != -1):
			midiName = temp[temp.find("client")+7:temp.find("[type")-1]
			midiList.append(midiName)
			temp = temp[temp.find('[type')+4:length]
		midiList=midiList[1:len(midiList)-1]
	return 	midiList

def command(command):
	print("oui")
	temp =os.popen(str(command)).read()
	print(temp)
	#os.system(command)

#____________________WIFI____________________#
def getWifi():
	ipadress = os.popen("hostname -I").read()
	ipadress = ipadress.split(' ')[0]
	ssid = os.popen("iwconfig wlan0 \
                | grep 'ESSID' \
                | awk '{print $4}' \
                | awk -F\\\" '{print $2}'").read()
	return [ipadress,ssid]
