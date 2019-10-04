import numpy as np
import cv2
from mss import mss
import win32.win32gui as win32gui
import pythonwin.win32ui as win32ui
from ctypes import windll
from tkinter import *
from PIL import Image

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

def previewWindow(window):
    while 1:
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
            cv2.imshow('test', np.array(im))
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

def callback(window, list): # Callback for EnumWindows; appends the window to the list
    list.append(window)

rawWindowList = []
win32gui.EnumWindows(callback, rawWindowList)
windowList = list(filter(lambda window: isAltTabWindow(window), rawWindowList))
windowNames = list(map(lambda window: win32gui.GetWindowText(window), windowList))

master = Tk()

variable = StringVar(master)
variable.set('Select a window to capture' if len(windowNames) > 0 else 'No windows available') # default value

w = OptionMenu(master, variable,
    *(windowNames if len(windowNames) > 0 else ['No windows available']),
    command=(lambda windowName: previewWindow(win32gui.FindWindow(None, windowName)))
)
w.pack()

mainloop()

# mon = {'top': 160, 'left': 160, 'width': 200, 'height': 200}

# sct = mss()

# while 1:
#     sct_img = sct.grab(mon)
#     cv2.imshow('test', np.array(sct_img))
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break
