import pyautogui
import threading

import pystray
from PIL import Image

from config.config_manager import ConfigManager
from create_icons import get_cpu_mem_icon, get_net_disk_icon
from double_click_manager import DoubleClickManager
from stats import DeviceStats


def update_status_loop(icm, ind):
    """ Update icon images and messages """
    config = ConfigManager('./config.ini')
    stats = DeviceStats()
    while True:
        stats.update_stats()
        icm.icon, icm.title = get_cpu_mem_icon(stats, config)
        ind.icon, ind.title = get_net_disk_icon(stats, config)


def exit_action(icm, ind):
    icm.visible = False
    ind.visible = False
    icm.stop()
    ind.stop()


def open_task_manager():
    pyautogui.hotkey('ctrl', 'shift', 'esc')


def click_action():
    if DoubleClickManager.check_double_click():
        open_task_manager()


def create_icons():
    icon_cm = pystray.Icon('cpu_mem')
    icon_nd = pystray.Icon('net_disk')
    icon_cm.menu = icon_nd.menu = pystray.Menu(
        pystray.MenuItem('Task manager - click', lambda: click_action(), default=True, visible=False),
        pystray.MenuItem('Task manager', lambda: open_task_manager()),
        pystray.MenuItem('Exit', lambda: exit_action(icon_cm, icon_nd)),
    )
    icon_cm.icon = Image.new('RGBA', (16, 16), '#ffffff00')
    icon_nd.icon = Image.new('RGBA', (16, 16), '#ffffff00')
    return icon_cm, icon_nd


def main():
    icon_cm, icon_nd = create_icons()
    t_cm = threading.Thread(target=lambda: icon_cm.run(), name='cpu_mem_icon', daemon=True)
    t_nd = threading.Thread(target=lambda: icon_nd.run(), name='net_disk_icon', daemon=True)
    t_status = threading.Thread(target=update_status_loop, args=(icon_cm, icon_nd,), name='kool_updater', daemon=True)
    t_status.start()
    # Start 1st network/disk so its icon is on the right of the cpu/mem one
    # ... not always work
    t_nd.start()
    t_cm.start()
    t_nd.join()
    t_cm.join()


if __name__ == '__main__':
    main()
