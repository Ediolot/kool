import numpy as np
from PIL import Image

from draw_tools import draw_vline, draw_hline


def get_cpu_mem_icon(stats, config):
    image = np.zeros((16, 16, 4), dtype=np.uint8)

    draw_seps = config.get_bool('misc/draw_separators')
    mem_color = config.get_color_pair('memory')
    cpu_color = config.get_color_pair('cpu')

    mem_usage = max((stats['memory'] / 100) * 16, 1)  # Set memory usage as a value in [1, 16]
    cpu_usage = [max((usage / 100) * 14, 1) for usage in stats['cpu']['all']]  # Set cpu usage as a value in [1, 14]
    cpu_line_width = 16 // len(cpu_usage)

    # Draw
    draw_hline(image, 0, mem_usage, 0, 2, mem_color[0])
    draw_hline(image, mem_usage, 16, 0, 2, mem_color[1])
    for i, usage in enumerate(cpu_usage):
        draw_vline(image, 0, usage, i * cpu_line_width, cpu_line_width, cpu_color[0], draw_separator=draw_seps)
        draw_vline(image, usage, 14, i * cpu_line_width, cpu_line_width, cpu_color[1], draw_separator=draw_seps)

    image = np.ascontiguousarray(image)
    image = Image.fromarray(image, 'RGBA')
    txt = f'CPU {stats["cpu"]["avg"]:.2f}%\n' \
          f'MEM {stats["memory"]:.2f}%'
    return image, txt


def get_net_disk_icon(stats, config):
    image = np.zeros((16, 16, 4), dtype=np.uint8)

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
    for k in range(4):
        name, (size, color) = io_order[k]
        draw_vline(image, 0, size, k * 4, 4, color[0], draw_separator=draw_seps)
        draw_vline(image, size, 16, k * 4, 4, color[1], draw_separator=draw_seps)

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
