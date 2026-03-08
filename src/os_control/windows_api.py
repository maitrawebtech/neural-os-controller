import win32gui
import win32con
import win32api
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

VK_LWIN = 0x5B
VK_LCONTROL = 0xA2
VK_LEFT = 0x25
VK_RIGHT = 0x27

class WindowsController:
    def __init__(self):
        # Setup pycaw for volume control
        try:
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"Failed to initialize audio: {e}")
            self.volume = None
            
        # Hide console if needed (optional)

    def get_foreground_window(self):
        return win32gui.GetForegroundWindow()

    def get_window_rect(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            return x, y, w, h
        except:
            return 0, 0, 0, 0

    def move_window(self, hwnd, x, y, w, h):
        try:
            win32gui.MoveWindow(hwnd, int(x), int(y), int(w), int(h), True)
        except Exception as e:
            pass # Handle desktop or special windows we can't move

    def set_window_opacity(self, hwnd, opacity):
        """Opacity from 0.0 to 1.0"""
        try:
            # Add WS_EX_LAYERED to window style
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style | win32con.WS_EX_LAYERED)
            
            alpha = int(opacity * 255)
            # SetLayeredWindowAttributes(hwnd, crKey, bAlpha, dwFlags)
            win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)
        except Exception as e:
            pass

    def minimize_window(self, hwnd):
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
        except:
            pass

    def switch_virtual_desktop(self, direction="right"):
        """Simulates Win+Ctrl+Left/Right"""
        # Key down
        win32api.keybd_event(VK_LWIN, 0, 0, 0)
        win32api.keybd_event(VK_LCONTROL, 0, 0, 0)
        
        if direction == "right":
            win32api.keybd_event(VK_RIGHT, 0, 0, 0)
            win32api.keybd_event(VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            win32api.keybd_event(VK_LEFT, 0, 0, 0)
            win32api.keybd_event(VK_LEFT, 0, win32con.KEYEVENTF_KEYUP, 0)
            
        # Key up
        win32api.keybd_event(VK_LCONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)

    def execute_stealth_protocol(self):
        """Mutes volume and shows desktop"""
        if self.volume:
            self.volume.SetMute(1, None)
            
        # Show desktop (Win+D)
        win32api.keybd_event(VK_LWIN, 0, 0, 0)
        win32api.keybd_event(ord('D'), 0, 0, 0)
        win32api.keybd_event(ord('D'), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)
