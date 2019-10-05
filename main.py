import numpy as np
import cv2
from mss import mss
import win32.win32gui as win32gui
import pythonwin.win32ui as win32ui
from ctypes import windll
from tkinter import *
from tkinter import _setit
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
            cv2.imshow('Screen capture preview - press "q" to quit', np.array(im))
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

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
    optionMenu.pack()

    mainloop()

def main():
    initGui()

if __name__ == "__main__":
    main()
