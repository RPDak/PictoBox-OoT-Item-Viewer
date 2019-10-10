from __future__ import print_function
import numpy as np
import cv2
from mss import mss
import win32.win32gui as win32gui
import pythonwin.win32ui as win32ui
from ctypes import windll
from tkinter import *
from tkinter import _setit
from PIL import Image
from pygrabber.dshow_graph import FilterGraph
from keras.models import load_model

# local modules
from pictobox.model import CLASS_NAMES, normalizeImage, flipChannels

GWL_EXSTYLE = -20
WS_EX_WINDOWEDGE = 256

def isAltTabWindow(window):
    """Whether or not the window handle is of a window that would appear in the alt-tab list.

    EnumWindows does a big brain move and enums a bunch of useless 'windows' that we need to
    filter out. You can use this function in combination with filter()

    Args:
        window (HWND): The window handle to check.

    Returns:
        bool: True if the window is an alt-tab window.

    """
    if (not win32gui.IsWindowVisible(window)):
        return False

    if (win32gui.GetParent(window)):
        return False

    if (win32gui.GetWindowLong(window, GWL_EXSTYLE) is not WS_EX_WINDOWEDGE): # These numbers were from the win32 documentation
        return False

    return True

def findVideoDevice():
    graph = FilterGraph()
    deviceNum = len(graph.get_input_devices())
    if 'OBS-Camera' in graph.get_input_devices():
        defaultDevice = graph.get_input_devices().index('OBS-Camera')
    else:
        defaultDevice = 'NoCam'
    return defaultDevice

def showVideoDevice():
    if findVideoDevice() != 'NoCam':
        cap = cv2.VideoCapture(findVideoDevice())
        while(True):        
            ret,frame = cap.read()
            fHeight, fWidth, fChannels = frame.shape
            #Crop just the items
            croppedFrame1 = frame[35:84, 458:507]
            croppedFrame2 = frame[69:118, 501:551]
            croppedFrame3 = frame[37:86, 543:595]
            combo = np.concatenate((croppedFrame1, croppedFrame2, croppedFrame3), axis=1)
            cv2.imshow('camera - press q to close',combo)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()         
    else:
        root2= Tk()
        root2.title("Warning")
        text1 = Text(root2, height=2, width=45)
        
        text1.config(state="normal")
        text1.insert(INSERT,"Warning: OBS Virtual Camera is not detected.")
        text1.config(state="disabled")
        
        text1.pack()
        
        root2.mainloop()
        

def previewWindow(window):
    model = load_model('pictobox/model/model.h5')

    while window:
        rect = win32gui.GetClientRect(window)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]

        # Duplicate the Device Context (DC) of the window to capture
        windowDC = win32gui.GetWindowDC(window)
        copyDC  = win32ui.CreateDCFromHandle(windowDC)
        
        # Create a bitmap to hold the window capture image
        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(copyDC, w, h)

        # Create a separate DC to save the bitmap and capture the image
        saveDC = copyDC.CreateCompatibleDC()
        saveDC.SelectObject(saveBitMap)
        result = windll.user32.PrintWindow(window, saveDC.GetSafeHdc(), 1)

        if result == 1: # Success

            # Transform the bitmap into an Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'RGBX', 0, 1)

            # Release the memory of the objects we no longer need
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            copyDC.DeleteDC()
            win32gui.ReleaseDC(window, windowDC)

            # Display the image
            
            winHeight = im.height
            winWidth = im.width
            
            #Set new width to 640 and height to a corresponding number
            newWinHeight = round((640/winWidth)*winHeight)
            baseWidth = 640
            
            resizedWindow = im.resize((baseWidth,newWinHeight), Image.ANTIALIAS)
            
            #Crop just the items
            croppedWin1 = resizedWindow.crop((458, 35, 507, 84))
            croppedWin2 = resizedWindow.crop((501, 69, 551, 118))
            croppedWin3 = resizedWindow.crop((543, 37, 595, 86))

            normalized1 = normalizeImage(croppedWin1)
            predictions1 = model.predict(normalized1)
            class1 = CLASS_NAMES[np.argmax(predictions1)]
            certainty1 = float(np.max(predictions1))

            normalized2 = normalizeImage(croppedWin2)
            predictions2 = model.predict(normalized2)
            class2 = CLASS_NAMES[np.argmax(predictions2)]
            certainty2 = float(np.max(predictions2))

            normalized3 = normalizeImage(croppedWin3)
            predictions3 = model.predict(normalized3)
            class3 = CLASS_NAMES[np.argmax(predictions3)]
            certainty3 = float(np.max(predictions3))

            print(class1, certainty1, class2, certainty2, class3, certainty3)
            
            winCombo = np.concatenate((croppedWin1, croppedWin2, croppedWin3), axis=1)            
            
            cv2.imshow('Screen capture preview - press "q" to quit', np.array(winCombo))

            keyPressed = cv2.waitKey(25) & 0xFF
            if keyPressed == ord('q'):
                cv2.destroyAllWindows()
                break
            elif keyPressed == ord('1'):
                flipChannels(croppedWin1).save('c_left.jpg')
            elif keyPressed == ord('2'):
                flipChannels(croppedWin2).save('c_down.jpg')
            elif keyPressed == ord('3'):
                flipChannels(croppedWin3).save('c_right.jpg')

def getWindowNames():
    """A list of window names as per win32gui.GetWindowText()

    Returns:
        list of str: A list of names of available windows.

    """
    rawWindowList = []
    win32gui.EnumWindows(lambda window, list: list.append(window), rawWindowList)
    windowList = list(filter(lambda window: isAltTabWindow(window), rawWindowList))
    return list(map(lambda window: win32gui.GetWindowText(window), windowList))

def updateOptionMenuOptions(optionMenu, variable, options, callback):
    """Updates the OptionMenu with a new list of options

        Args:
            optionMenu (OptionMenu): The OptionMenu to update.
            variable (StringVar): The associated string variable label for optionMenu.
            options (list of str): The new options.
            callback (Function): The callback function for when an option is selected.
    """
    menu = optionMenu.children['menu']
    menu.delete(0, 'end')
    for option in options:
        menu.add_command(label=option, command=_setit(variable, option, callback))

def initGui():
    """Initialize the GUI
    """
    root = Tk()
    root.geometry("300x100")

    initialWindowNames = getWindowNames()
    optionMenuLabel = StringVar(root)
    optionMenuLabel.set('Select a window to capture' if len(initialWindowNames) > 0 else 'No windows available') # default value

    optionMenu = OptionMenu(root, optionMenuLabel, *(initialWindowNames if len(initialWindowNames) > 0 else ['No windows available']))
    optionMenu.bind( # Refrshes the options everytime the menu is opened
        '<Button-1>',
        lambda event: updateOptionMenuOptions(optionMenu, optionMenuLabel, getWindowNames(),
        lambda windowName: previewWindow(win32gui.FindWindow(None, windowName)))
    )
    
    vidButton = Button(root, text="Webcam", command=showVideoDevice)
        
    vidButton.pack()    
    optionMenu.pack()

    mainloop()

def main():
    initGui()

if __name__ == "__main__":
    main()
