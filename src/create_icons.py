from PIL import Image, ImageDraw


def half_opacity(color):
    return color[0], color[1], color[2], color[3] // 2


def get_cpu_mem_icon(stats, config, memory_width=2):
    draw_seps = config.get_bool('misc/draw_separators')
    mem_color = config.get_color_pair('memory')
    cpu_color = config.get_color_pair('cpu')

    cpu_bar_height = 16 - memory_width
    mem_usage = max(stats['memory'] * 16 / 100, 1)  # Memory in range [1, 16]
    cpu_usage = [max(usage * cpu_bar_height / 100, 1) for usage in stats['cpu']['all']]  # CPU usage in range [1, cpu_bar_height]
    cpu_bar_width = 16 // len(cpu_usage)

    image = Image.new('RGBA', (16, 16))
    dc = ImageDraw.Draw(image)

    dc.rectangle((0, 0, 16, memory_width), mem_color[1])
    dc.rectangle((0, 0, mem_usage, memory_width - 1), mem_color[0])
    for i, usage in enumerate(cpu_usage):
        x = i * cpu_bar_width

        if draw_seps:
            dc.rectangle((x, 16, x + cpu_bar_width - 1, 16 - cpu_bar_height), fill=half_opacity(cpu_color[1]))
            dc.rectangle((x, 16, x + cpu_bar_width - 2, 16 - cpu_bar_height), fill=cpu_color[1])
            dc.rectangle((x, 16 - usage, x + cpu_bar_width - 1, 16), fill=half_opacity(cpu_color[0]))
            dc.rectangle((x, 16 - usage, x + cpu_bar_width - 2, 16), fill=cpu_color[0])
        else:
            dc.rectangle((x, 16, x + cpu_bar_width - 1, 16 - cpu_bar_height), fill=cpu_color[1])
            dc.rectangle((x, 16 - usage, x + cpu_bar_width - 1, 16), fill=cpu_color[0])

    return image, f'CPU: {stats["cpu"]["avg"]:.2f}%\nMEM: {stats["memory"]:.2f}%'


def get_net_disk_icon(stats, config, lines_width=4):
    draw_seps = config.get_bool('misc/draw_separators')
    # Get stats in range [1, 16]
    network_sent = max(stats['network']['sent'] * 16 / 100, 1)
    network_recv = max(stats['network']['recv'] * 16 / 100, 1)
    disk_read = max(stats['disk']['read'] * 16 / 100, 1)
    disk_write = max(stats['disk']['write'] * 16 / 100, 1)

    network_sent_color = config.get_color_pair('network_sent')
    network_recv_color = config.get_color_pair('network_recv')
    disk_write_color = config.get_color_pair('disk_write')
    disk_read_color = config.get_color_pair('disk_read')

    io_order = {
        config.get_int('io_order/network_sent'): ('network_sent', stats['network']['raw_sent'], (network_sent, network_sent_color)),
        config.get_int('io_order/network_recv'): ('network_recv', stats['network']['raw_recv'], (network_recv, network_recv_color)),
        config.get_int('io_order/disk_write'): ('disk_write', stats['disk']['raw_write'], (disk_write, disk_write_color)),
        config.get_int('io_order/disk_read'): ('disk_read', stats['disk']['raw_read'], (disk_read, disk_read_color)),
    }

    txt = ''
    network_done = False
    disk_done = False
    image = Image.new('RGBA', (16, 16))
    dc = ImageDraw.Draw(image)
    for k in range(4):
        name, value, (size, color) = io_order[k]

        x = lines_width * k
        if draw_seps:
            dc.rectangle((x, 0, x + lines_width - 1, 16), fill=half_opacity(color[1]))
            dc.rectangle((x, 0, x + lines_width - 2, 16), fill=color[1])
            dc.rectangle((x, 16 - size, x + lines_width - 1, 16), fill=half_opacity(color[0]))
            dc.rectangle((x, 16 - size, x + lines_width - 2, 16), fill=color[0])
        else:
            dc.rectangle((x, 0, x + lines_width - 1, 16), fill=color[1])
            dc.rectangle((x, 16 - size, x + lines_width - 1, 16), fill=color[0])

        # TODO
        units = ''
        if value > 999:
            value = value / 1024
            units = 'K'
        if value > 999:
            value = value / 1024
            units = 'M'

        direction = 'ERROR'     # Default value, just in case
        if name == 'network_sent' or name == 'disk_write':
            direction = '⯅' # ↑
        elif name == 'network_recv' or name == 'disk_read':
            direction = '⯆' # ↓

        if 'network' in name and not network_done:
            network_done = True
            if disk_done:
                txt += '\n'
            txt += 'N:'
        if 'disk' in name and not disk_done:
            disk_done = True
            if network_done:
                txt += '\n'
            txt += 'D:'

        txt += f' {direction} {value:1.0f} {units}B/s'

    return image, txt
