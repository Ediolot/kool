from PIL import Image, ImageDraw


def get_cpu_mem_icon(stats, config):
    draw_seps = config.get_bool('misc/draw_separators')
    mem_color = config.get_color_pair('memory')
    cpu_color = config.get_color_pair('cpu')

    mem_usage = int(stats['memory'] * 16 / 100 + 0.9)  # Round to next int
    cpu_usage = [int(usage * 14 / 100 + 0.9) for usage in stats['cpu']['all']]  # Set cpu usage as a value in [1, 14]
    cpu_bar_width = 16 // len(cpu_usage)

    image = Image.new('RGBA', (16, 16))
    dc = ImageDraw.Draw(image)
    dc.rectangle((mem_usage, 0, 16, 2 - 1), mem_color[1])
    dc.rectangle((0, 0, max(mem_usage, 1), 2 - 1), mem_color[0])
    for i, usage in enumerate(cpu_usage):
        x = i * cpu_bar_width
        dc.rectangle((x, 16 - usage,  + cpu_bar_width - 1, 16 - 14), fill=cpu_color[1])
        # rectangle at least draw one pixel
        dc.rectangle((x, 16, x + cpu_bar_width - 1, min(16 - usage, 15)), fill=cpu_color[0])
    txt = f'CPU {stats["cpu"]["avg"]:.2f}%\n' \
          f'MEM {stats["memory"]:.2f}%'
    return image, txt


def get_net_disk_icon(stats, config):
    draw_seps = config.get_bool('misc/draw_separators')
    # Get stats in range [1, 16]
    network_sent = int(stats['network']['sent'] * 16 / 100 + 0.9)   # Round to next int
    network_recv = int(stats['network']['recv'] * 16 / 100 + 0.9)
    disk_read = int(stats['disk']['read'] * 16 / 100 + 0.9)
    disk_write = int(stats['disk']['write'] * 16 / 100 + 0.9)

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
        x = 4 * k
        dc.rectangle((x, 16 - size, x + 4 - 1, 0), fill=color[1])
        # rectangle at least draw one pixel
        dc.rectangle((x, 16, x + 4 - 1, min(16 - size, 15)), fill=color[0])
        # dc.rectangle([x, 16, x + 4, 0], outline='white')

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
