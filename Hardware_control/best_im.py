"""
@Prosimios, 2022.

The aim of this script is to take highest signal images.

This code take images with increasing Shutter Speed (SS) until
the image get saturated (i.e. at least one pixel reach 255 value)
or the maximum shutter speed is reached (it reach a maximum because it
depends on the specified frame rate)
Between each image the shutter speed is increased by a step equal
to the initial value (3er argument).

Ones the procedure retrieves an image with a saturated value (maximum pixel 
value reached), the image is refined by reducing/increasing cicles of previous
shutter speed step value by half. The cicle is repeated until shutter speed is 
under the input minimal allowed value (min_ss_step).

Also the code stop if the shutter speed increase until it maximum (even if max
pixel value was not reached)

"""

## Import packages ##
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
import os
import sys
from shutil import copyfile
import matplotlib.pyplot as plt


# Parameters that could be modified by the user
MAX_VALUE = 255         # pixel value to reach

if MAX_VALUE > 255 or MAX_VALUE <0:
    print('\nInvalid maximmum pixel value. It should be between [0,255]')
    print('Please, modify it in the code')
    sys.exit()

######### LED GPIO setting ###########
pin = 29

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

camera = PiCamera()

#########################################

# Example of running the code
# python3 best_image.py gel_13_5_21 image 100000 10000 100 

param_msj = "Required parameters: folder name, filename, initial shutter speed,"\
           "(microsecs), min_ss_step (microsecs), ISO (100 to 800)"

if len(sys.argv) == 6:
    try:
        folder = sys.argv[1]
        filename = sys.argv[2] 
        ss = int(sys.argv[3])
        min_step = int(sys.argv[4])  #min ss_step used to refine the image
        iso = int(sys.argv[5]) 

        while iso < 100 or iso > 800:
            print('invalid ISO. Values should be between 100 - 800')
            iso = input('Enter new iso value: ')

    except:

        print('Some parameter(s) seems to be invalid.')
        print (param_msj)
        sys.exit()

else:
    print (param_msj )
    sys.exit()

# if folder is not present in the current directory, then create the folder
if folder not in os.listdir('.'):
    
    os.mkdir(folder)  #create the folder
    print('\nFolder', folder, 'was created\n')
    
# Minimal camera settings
camera.resolution=(960,720)
camera.ISO= iso
camera.shutter_speed = ss       # exposure time in microsecs e.g. 100000
camera.exposure_mode = 'off'    #'fixedfps'
camera.awb_gains = [1,1]
camera.awb_mode = 'off'

print('ISO:', camera.ISO)

############################
# Advanced camera users:
# -------------------------------------------------------------
# These are other possible parameters to change, depending on experiment:

camera.framerate = 1        # frames/sec, determines the max shutter speed
#camera.analog_gain = 1
#camera.digital_gain=1
#camera.brightness = 50
#camera.sharpness = 0
#camera.contrast = 0              # useful to reduce the background
#camera.saturation = 0
#camera.exposure_compensation=0
#camera.image_effect='none'
#camera.color_effects=None
#camera.exposure_speed

# Save this file with the data (to record settings etc.)
scriptpath = os.path.dirname(os.path.realpath(__file__))
copyfile(os.path.join(scriptpath, sys.argv[0]), os.path.join(folder, 'script.py'))


# turn the LEDs on            
GPIO.output(pin,GPIO.HIGH)

# Run the image capture loop

c = 0  # counter
ss_step = int(camera.shutter_speed)  #ss_step is the same as the initial value
token = False        # change at reach max_px = MAX_VALUE (e.g. 255)

while True:

    css = camera.shutter_speed   # efective camera shutter speed

    print('\nCycle ' + str(c))
    print('Shutter speed:', str(css))
    # if the effective shutter speed doesnt coincide with the one you set,
    # you must modify the camera.framerate parameter.


    #datestr = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    #fname = os.path.join(folder, datestr + "_" + filename + "_%04d.jpg"%(i))
    fname = os.path.join(folder, filename+'_'+str(iso) + '_'+ str(css)+'.jpg') #"_%04d.jpg"%(i))
    camera.capture(fname)

    imagen = plt.imread(fname)
    max_px = imagen.max()
    min_px = imagen.min()
    print('max pixel value: ',max_px)
    print('min pixel value: ',min_px)

    # SS incrementation
    if max_px == MAX_VALUE:
        token = True
        
        if ss_step > min_step:

            ss_step = int(ss_step/2)

            camera.shutter_speed -= ss_step

            os.remove(fname)   # remove the previous image

        else:

            break
        
    else:
        if token == True:
            ss_step = int(ss_step/2)
            token = False
            
        camera.shutter_speed += ss_step

        if camera.shutter_speed == css:
            print('\nmaximum shutter speed reached')
            break
        else:
            os.remove(fname)   # remove the previous image


    #cycle update
    c+=1


#turn the LEDs off
GPIO.output(pin,GPIO.LOW)    
GPIO.cleanup()
