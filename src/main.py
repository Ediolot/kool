"""
https://pystray.readthedocs.io/en/latest/usage.html

Update/change Icon.image while it is running
https://github.com/moses-palmer/pystray/issues/68
"""


import pystray
from PIL import Image, ImageDraw
import threading
from time import sleep
from stats import DeviceStats
from config.config_manager import ConfigManager
from create_icons import get_cpu_mem_icon, get_net_disk_icon

# def create_image():
#     width = 16
#     height = 16
#     color1 = 0x0080ff
#     color2 = 0x80ff00

#     # Generate an image and draw a pattern
#     image = Image.new('RGB', (width, height), color1)
#     dc = ImageDraw.Draw(image)
#     dc.rectangle(
#         (width // 2, 0, width, height // 2),
#         fill=color2)
#     dc.rectangle(
#         (0, height // 2, width // 2, height),
#         fill=color2)
#     return image

def create_image(color1, color2, width=64, height=64):
    image = Image.new('RGBA', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

# def update_status_loop(tp1, tp2):
#     """ Update icon images and messages """
#     config = ConfigManager('./config.ini')
#     stats = DeviceStats()
#     while True:
#         stats.update_stats()
#         icon_cpu_mem, cpu_mem_text = get_cpu_mem_icon(stats, config)
#         icon_net_disk, net_disk_text = get_net_disk_icon(stats, config)
#         with lock:
#             tp1.set_trail_icon(icon_cpu_mem, cpu_mem_text)
#             tp2.set_trail_icon(icon_net_disk, net_disk_text)
#             tp1.post_message(Message.REFRESH_ICON.value)
#             tp2.post_message(Message.REFRESH_ICON.value)

def update_status_loop(icm, ind):
    """ Update icon images and messages """
    config = ConfigManager('./config.ini')
    stats = DeviceStats()
    while True:
        stats.update_stats()
        icm.icon, icm.title = get_cpu_mem_icon(stats, config)
        ind.icon, ind.title = get_net_disk_icon(stats, config)
        # ind.icon = icon_net_disk
    # flag = 0
    # while True:
    #     if flag:
    #         flag = 0
    #         icm.icon = create_image('green', 'orange')
    #         ind.icon = create_image('white', 'black')
    #     else:
    #         flag = 1
    #         icm.icon = create_image('white', 'black')
    #         ind.icon = create_image('green', 'orange')
    #     sleep(1)
    return

def icon_run(icon):
    icon.run()

def exit_action(icm, ind):
    icm.visible = False
    ind.visible = False
    icm.stop()
    ind.stop()

def main():
    icon_cm = pystray.Icon('cpu_mem')
    icon_nd = pystray.Icon('net_disk')
    icon_cm.menu = pystray.Menu(
        pystray.MenuItem('Exit', lambda : exit_action(icon_cm, icon_nd)),
    )
    icon_nd.menu = icon_cm.menu
    icon_cm.icon = create_image('white', 'black')
    icon_nd.icon = create_image('green', 'orange')
    t_cm = threading.Thread(target=icon_run, name='ir',
                            args=(icon_cm,), daemon=True)
    t_cm.start()
    sleep(0.2)        # Make sure 2nd icon is placed on the right of the 1st one
    t_status = threading.Thread(target=update_status_loop, name='usl',
                                args=(icon_cm, icon_nd,), daemon=True)
    t_status.start()
    # t_nd = threading.Thread(target=icon_run, args=(icon_nd,), daemon=True)
    # t_nd.start()
    icon_nd.run()   # Seem it needs an icon.run() in main

if __name__ == '__main__':
    main()
