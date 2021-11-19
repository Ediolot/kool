""" Disk usage bar tests """

import os
from enum import Enum
from tempfile import mkstemp

import win32api
import win32con
import win32gui
from PIL import Image


class Message(Enum):
    EXIT = 1023
    REFRESH_ICON = 1026


class Tooltip:
    def __init__(self, name=''):
        win32gui.InitCommonControls()
        self.should_exit = False
        self.name = name
        self.icon_set = False
        fd, self.icon = mkstemp(suffix='.ico')
        os.close(fd)  # Close the file descriptor, we just need an unique path
        self.style = win32con.WS_OVERLAPPEDWINDOW | win32con.WS_SYSMENU
        self.instance_handle = win32api.GetModuleHandle(None)  # Handle instance to the current executable
        self.window_class = self._create_window_class(self._build_function_map(), register=True)
        self.window_handle = self._create_window(update=True)

    def cleanup(self):
        nid = (self.window_handle, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)
        os.remove(self.icon)

    def _create_window_class(self, message_map, register=False):
        wc = win32gui.WNDCLASS()
        wc.hInstance = self.instance_handle  # Set the parent process to us
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.lpfnWndProc = message_map
        wc.lpszClassName = self.name
        if register:
            win32gui.RegisterClass(wc)
        return wc

    def _create_window(self, update=True):
        handle = win32gui.CreateWindow(
            self.window_class.lpszClassName,
            self.name,
            self.style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            self.instance_handle,
            None,
        )
        if update:
            win32gui.UpdateWindow(handle)
        return handle

    def _build_function_map(self):
        taskbar_restart_msg = win32gui.RegisterWindowMessage("TaskbarCreated")
        return {
            taskbar_restart_msg: self.on_restart,
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_taskbar_notify,
        }

    def set_trail_icon(self, icon: Image.Image, name: str = None):
        icon.save(self.icon)
        if name:
            self.name = name

    def refresh_icon(self):
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(self.instance_handle,
                                   self.icon,
                                   win32con.IMAGE_ICON,
                                   0,
                                   0,
                                   icon_flags)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.window_handle, 0, flags, win32con.WM_USER + 20, hicon, self.name)
        action = win32gui.NIM_MODIFY if self.icon_set else win32gui.NIM_ADD
        win32gui.Shell_NotifyIcon(action, nid)
        self.icon_set = True

    def post_message(self, msg: Message):
        win32gui.PostMessage(self.window_handle, win32con.WM_COMMAND, msg, 0)

    def on_restart(self, hwnd, msg, wparam, lparam):
        pass

    def on_destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.window_handle, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)

    def on_taskbar_notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_RBUTTONUP:
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, Message.EXIT.value, "Exit")
            pos = win32gui.GetCursorPos()
            # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
            win32gui.SetForegroundWindow(self.window_handle)
            win32gui.TrackPopupMenu(
                menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.window_handle, None
            )
            win32gui.PostMessage(self.window_handle, win32con.WM_NULL, 0, 0)
        return 1

    def on_command(self, hwnd, msg, wparam, lparam):
        msg_id = win32api.LOWORD(wparam)
        if msg_id == Message.EXIT.value:
            self.should_exit = True
        elif msg_id == Message.REFRESH_ICON.value:
            self.refresh_icon()
        else:
            print("Unknown command -", msg_id)
