import threading
import time

import win32gui

from config.config_manager import ConfigManager
from create_icons import get_cpu_mem_icon, get_net_disk_icon
from stats import DeviceStats
from tooltip import Tooltip, Message

lock = threading.RLock()  # Lock for updating ico image and messages


def update_status_loop(tp1, tp2):
    """ Update icon images and messages """
    config = ConfigManager('./config.ini')
    stats = DeviceStats()
    while True:
        stats.update_stats()
        icon_cpu_mem, cpu_mem_text = get_cpu_mem_icon(stats, config)
        icon_net_disk, net_disk_text = get_net_disk_icon(stats, config)
        with lock:
            tp1.set_trail_icon(icon_cpu_mem, cpu_mem_text)
            tp2.set_trail_icon(icon_net_disk, net_disk_text)
            tp1.post_message(Message.REFRESH_ICON.value)
            tp2.post_message(Message.REFRESH_ICON.value)


def update_window_loop(tp1, tp2):
    """ Loop to update the window (trail icon) status """
    try:
        while not tp1.should_exit and not tp2.should_exit:
            time.sleep(0.1)  # Wait instead of using blocking messages so we can check exit variable and free the lock
            with lock:
                win32gui.PumpWaitingMessages()
    except KeyboardInterrupt:
        return


def main():
    tp1 = Tooltip('CPU/MEM Meter')
    tp2 = Tooltip('NET/DISK Meter')
    status_loop = threading.Thread(target=update_status_loop, args=(tp1, tp2), daemon=True)
    status_loop.start()
    update_window_loop(tp1, tp2)
    tp1.cleanup()
    tp2.cleanup()


if __name__ == '__main__':
    main()
