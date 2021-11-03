
kDefaultConfig = {
    'colors': {
        # Hex rgba format
        'cpu': 'ff5151ff',
        'memory': 'ff9b6aff',
        'network_sent': '6699ccff',
        'network_recv': 'fff275ff',
        'disk_read': 'ff8c42ff',
        'disk_write': 'ff3c38ff',
    },
    'background_colors': {
        # Hex rgba format
        'cpu': 'ffffff00',
        'memory': 'ffffff00',
        'network_sent': 'ffffff00',
        'network_recv': 'ffffff00',
        'disk_read': 'ffffff00',
        'disk_write': 'ffffff00',
    },
    'maximums': {
        # Units in MB/s
        'network_sent': 25,
        'network_recv': 25,
        'disk_read': 25,
        'disk_write': 25,
    },
    'io_order': {
        # Order in which information is displayed for the second tooltip and message
        'network_sent': 0,
        'network_recv': 1,
        'disk_read': 2,
        'disk_write': 3,
    },
    'misc': {
        'draw_separators': True,
        'update_time_s': 3,
    }
}