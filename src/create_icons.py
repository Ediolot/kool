import numpy as np
from PIL import ImageColor
from PIL import Image

from draw_tools import draw_vline, draw_hline


def get_cpu_mem_icon(stats, config):
    image = np.zeros((16, 16, 4), dtype=np.uint8)

    draw_seps = config.getboolean('other', 'draw_separators', fallback=True)
    mem_color = ImageColor.getcolor('#' + config.get('colors', 'memory', fallback='ffffffff'), 'RGBA')
    cpu_color = ImageColor.getcolor('#' + config.get('colors', 'cpu', fallback='ffffffff'), 'RGBA')
    mem_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'memory', fallback='ffffff00'), 'RGBA')
    cpu_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'cpu', fallback='ffffff00'), 'RGBA')

    mem_usage = max((stats['memory'] / 100) * 16, 1)  # Set memory usage as a value in [1, 16]
    cpu_usage = [max((usage / 100) * 14, 1) for usage in stats['cpu']['all']]  # Set cpu usage as a value in [1, 14]
    cpu_line_width = 16 // len(cpu_usage)

    # Draw
    draw_hline(image, 0, mem_usage, 0, 2, mem_color)
    draw_hline(image, mem_usage, 16, 0, 2, mem_color_bk)
    for i, usage in enumerate(cpu_usage):
        draw_vline(image, 0, usage, i * cpu_line_width, cpu_line_width, cpu_color, draw_separator=draw_seps)
        draw_vline(image, usage, 14, i * cpu_line_width, cpu_line_width, cpu_color_bk, draw_separator=draw_seps)

    image = np.ascontiguousarray(image)
    image = Image.fromarray(image, 'RGBA')
    txt = f'CPU {stats["cpu"]["avg"]:.2f}%\n' \
          f'MEM {stats["memory"]:.2f}%'
    return image, txt


def get_net_disk_icon(stats, config):
    image = np.zeros((16, 16, 4), dtype=np.uint8)

    draw_seps = config.getboolean('other', 'draw_separators', fallback=True)
    # Get stats in range [1, 16]
    network_sent = max((stats['network']['sent'] / config.getint('maximums', 'network_sent', fallback=25)) * 16, 1)
    network_recv = max((stats['network']['recv'] / config.getint('maximums', 'network_recv', fallback=25)) * 16, 1)
    disk_read = max((stats['disk']['read'] / config.getint('maximums', 'disk_read', fallback=25)) * 16, 1)
    disk_write = max((stats['disk']['write'] / config.getint('maximums', 'disk_write', fallback=25)) * 16, 1)

    network_sent_color = ImageColor.getcolor('#' + config.get('colors', 'network_sent', fallback='ffffffff'), 'RGBA')
    network_recv_color = ImageColor.getcolor('#' + config.get('colors', 'network_recv', fallback='ffffffff'), 'RGBA')
    disk_read_color = ImageColor.getcolor('#' + config.get('colors', 'disk_read', fallback='ffffffff'), 'RGBA')
    disk_write_color = ImageColor.getcolor('#' + config.get('colors', 'disk_write', fallback='ffffffff'), 'RGBA')
    network_sent_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'network_sent', fallback='ffffffff'), 'RGBA')
    network_recv_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'network_recv', fallback='ffffffff'), 'RGBA')
    disk_read_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'disk_read', fallback='ffffffff'), 'RGBA')
    disk_write_color_bk = ImageColor.getcolor('#' + config.get('background_colors', 'disk_write', fallback='ffffffff'), 'RGBA')

    io_order = {}

    def try_add(name, data, fallback):
        key = config.getint('io_order', name, fallback=fallback)
        if key in io_order:
            print('Warning duplicated io_order, using fallback')
            key = fallback
        io_order[key] = (name, data)

    try_add('network_sent', (network_sent, network_sent_color, network_sent_color_bk), fallback=0)
    try_add('network_recv', (network_recv, network_recv_color, network_recv_color_bk), fallback=1)
    try_add('disk_read', (disk_read, disk_read_color, disk_read_color_bk), fallback=2)
    try_add('disk_write', (disk_write, disk_write_color, disk_write_color_bk), fallback=3)

    txt = ''
    network_done = False
    disk_done = False
    for k in range(4):
        name, (size, color, color_bk) = io_order[k]
        draw_vline(image, 0, size, k * 4, 4, color, draw_separator=draw_seps)
        draw_vline(image, size, 16, k * 4, 4, color_bk, draw_separator=draw_seps)

        # TODO
        if 'network' in name and not network_done:
            network_done = True
            if disk_done:
                txt += '  MB/s\n'
            txt += 'N:'
        if 'disk' in name and not disk_done:
            disk_done = True
            if network_done:
                txt += '  MB/s\n'
            txt += 'D:'
        if name == 'network_sent':
            txt += f' ↑ {stats["network"]["sent"]:3.0f}'
        if name == 'network_recv':
            txt += f' ↓ {stats["network"]["recv"]:3.0f}'
        if name == 'disk_read':
            txt += f' ↑ {stats["disk"]["read"]:3.0f}'
        if name == 'disk_write':
            txt += f' ↓ {stats["disk"]["write"]:3.0f}'
    txt += '  MB/s'

    image = np.ascontiguousarray(image)
    image = Image.fromarray(image, 'RGBA')
    return image, txt
