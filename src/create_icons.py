import numpy as np
from PIL import Image, ImageDraw

from draw_tools import draw_vline, draw_hline

def get_cpu_mem_icon(stats, config):
    draw_seps = config.get_bool('misc/draw_separators')
    mem_color = config.get_color_pair('memory')
    cpu_color = config.get_color_pair('cpu')

    mem_usage = max((stats['memory'] / 100) * 16, 1)  # Set memory usage as a value in [1, 16]
    cpu_usage = [max((usage / 100) * 14, 1) for usage in stats['cpu']['all']]  # Set cpu usage as a value in [1, 14]
    cpu_line_width = 16 // len(cpu_usage)

    image = Image.new('RGBA', (16, 16))
    dc = ImageDraw.Draw(image)
    dc.line([0, 0, mem_usage, 0], mem_color[0], 2)
    dc.line([mem_usage, 0, 16, 0], mem_color[1], 2)
    for i, usage in enumerate(cpu_usage):
        x = i * cpu_line_width
        dc.line([x, 16, x, 16 - usage], cpu_color[0], cpu_line_width)
        dc.line([x, 16 - usage, x, 16 - 14], cpu_color[1], cpu_line_width)
    txt = f'CPU {stats["cpu"]["avg"]:.2f}%\n' \
          f'MEM {stats["memory"]:.2f}%'
    return image, txt


def get_net_disk_icon(stats, config):
    draw_seps = config.get_bool('misc/draw_separators')
    # Get stats in range [1, 16]
    network_sent = max(stats['network']['sent'] / config.get_int('maximums/network_sent') * 16, 1)
    network_recv = max(stats['network']['recv'] / config.get_int('maximums/network_recv') * 16, 1)
    disk_read = max(stats['disk']['read'] / config.get_int('maximums/disk_read') * 16, 1)
    disk_write = max(stats['disk']['write'] / config.get_int('maximums/disk_write') * 16, 1)

    network_sent_color = config.get_color_pair('network_sent')
    network_recv_color = config.get_color_pair('network_recv')
    disk_read_color = config.get_color_pair('disk_read')
    disk_write_color = config.get_color_pair('disk_write')

    io_order = {
        config.get_int('io_order/network_sent'): ('network_sent', (network_sent, network_sent_color)),
        config.get_int('io_order/network_recv'): ('network_recv', (network_recv, network_recv_color)),
        config.get_int('io_order/disk_read'): ('disk_read', (disk_read, disk_read_color)),
        config.get_int('io_order/disk_write'): ('disk_write', (disk_write, disk_write_color)),
    }

    txt = ''
    network_done = False
    disk_done = False
    image = Image.new('RGBA', (16, 16))
    dc = ImageDraw.Draw(image)
    for k in range(4):
        name, (size, color) = io_order[k]
        # draw_vline(image, 0, size, k * 4, 4, color[0], draw_separator=draw_seps)
        # draw_vline(image, size, 16, k * 4, 4, color[1], draw_separator=draw_seps)
        # x = 4 * k
        # dc.line([x, 16, x, 16 - size], color[0], 4)
        # dc.line([x, 16 - size, x, 0], color[1], 4)
        x = 4 * k
        print(k, size)
        size=12
        dc.line([x, 16, x, 16 - size],'green', 4)
        dc.line([x, 16 - size, x, 0], 'red', 4)

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

    return image, txt
