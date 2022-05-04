#!/usr/bin/env python

import sys
import pulsectl
from gi.repository import Notify
import time

try:
    import launchpad_py as launchpad
except ImportError:
    try:
        import launchpad
    except ImportError:
        sys.exit("error loading launchpad.py")



Notify.init("LC-Volume")

notification = None
block_notification = False
t0= time.time()

###################################################################################################
# helper function to map 0-127 to 0-100
###################################################################################################
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


# e.g.:
# sink_name == Focusrite Swap
# normalized val [0-1]
def change_volume(sink_name, normalized_val):

    with pulsectl.Pulse('volume-increaser') as pulse:

        for sink in pulse.sink_list():
            #print(sink.description)
            
            # Focusrite
            # Focusrite Swap Front
            # Focusrite Dual Out
            # Focusrite Solo Front
            # Focusrite Solo Back
            # MusicBot
            
            if (sink.description) == sink_name:

                vol = sink.volume
                print((sink_name + ", " + str(vol)))
                # Make sure there are no big volume jumps when using initially
                if abs(vol.values[0]-normalized_val) > 0.05:
                    thisdoesnothing = 0
                else:
                    if "Focusrite Solo Front" == sink.description:
                        right_normalized_val = normalized_val * 0.85
                        newvol = pulsectl.PulseVolumeInfo([normalized_val, right_normalized_val])
                        pulse.volume_set(sink, newvol)
                    else:
                        pulse.volume_set_all_chans(sink, normalized_val)
                    

def change_input_volume(binary, normalized_val):
    with pulsectl.Pulse('volume-increaser') as pulse:
        for sink in pulse.sink_input_list():
            try:
                if sink.proplist['application.name'] == "QtPulseAudio:2633":
                    continue

                if sink.proplist['application.process.binary'] == binary:
                    vol = sink.volume
                    print((binary + ", " + str(vol)))
                    newvol = pulsectl.PulseVolumeInfo([normalized_val, normalized_val])
                    
                    pulse.volume_set(sink, newvol)
                    
            except KeyError:
                this = "doesnothing"
          
          

def set_knob(button_val, audiodevice, type, notification_title=""):
    
    global t0
    global block_notification
    global notification
    
    if notification_title == "":
        notification_title = audiodevice
        
    # map to 0-1
    normalized_val = (button_val / 127)

    if type == "input_volume":
        change_input_volume(audiodevice, normalized_val)
    elif type == "volume":
        change_volume(audiodevice, normalized_val)

    # Notification part

    summary = notification_title
    body = str(normalized_val)
                                
    current_time = time.time()

    # only update notification every ~200ms
    if current_time - t0 > 0.2:
        block_notification = False

    # close notification after 2 seconds - needed to work well
    if current_time - t0 > 2:
        try:
            notification.close()
            print("notification closed")
            
        except Exception:
            print("Error while closing notification")
                                
                                
    # only update notification if allowed...
    if not block_notification:
            t0= time.time()
            try:
                notification.update(
                    summary,
                    body, # Optional
                )
            except Exception:
                notification = Notify.Notification.new(
                    summary,
                    body, # Optional
                )
            try:
                notification.show()
            except:
                print("Error while showing notification!")

            block_notification = True


    return



def launch_control(tuple_list):
    
    global t0
    global block_notification
    global notification
    
    lp = launchpad.Launchpad()


    inName = "Launch Control"

    try:
        lp.Open( 0, inName )
    except:
        print("error opening this device")
        sys.exit(-1)

    t0= time.time()
    
    
    while(True):
        events = lp.EventRaw()
        if events != []:
            if len(events) == 1:
                
                # events, inner_event, valueblock are all lists
                for inner_event in events:


                    if len(inner_event) != 2:
                        print("somethings wrong with this inner value:")
                        print(inner_event)
                    else:
                        # watch this to understand:
                        #print(inner_event[0])
                        valueblock = inner_event[0]
                        
                        if len(valueblock) != 4:
                            print("somethings wrong with this valueblock!")
                            print(valueblock)
                            
                        # Those are all integer
                        device_id  = valueblock[0]
                        button_id  = valueblock[1]
                        button_val = valueblock[2]

                        # ID for Launch Control
                        if device_id == 182:
                            
                            for tuple_item in tuple_list:
                                #(28, "volume", "Focusrite", "Focusrite Master")
                                button_id_input, type, audiodevice, notification_title = tuple_item
                                if button_id == button_id_input:
                                    set_knob(button_val, audiodevice, type, notification_title)
                                    
                                    
            else:
                print("somethings wrong with this value:")
                print(events)

        # don't use too much cpu ressources - this line keeps cpu usage low
        time.sleep(0.001)

    



###################################################################################################


tuple_list = []


# Poti 8 oben -> Master Volume Focusrite
tuple_list.append((28, "volume", "Focusrite", "Focusrite Master"))

# Poti 8 unten -> Front Focusrite
tuple_list.append((48, "volume", "Focusrite Solo Front", "Focusrite Solo Front"))

# Poti 7 unten -> Back Focusrite
tuple_list.append((47, "volume", "Focusrite Solo Back", "Focusrite Solo Back"))

# Poti 6 unten -> Jellyfin Killerkeks
tuple_list.append((46, "input_volume", "media.killerkeks", "SK Killerkeks"))

# Poti 5 unten -> CsGo
tuple_list.append((45, "input_volume", "csgo_linux64", "Counter Strike: Global Offensive"))



launch_control(tuple_list)

