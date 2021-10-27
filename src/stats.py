from threading import RLock
from typing import Any, Dict

import numpy as np
import psutil


class DeviceStats:
    def __init__(self, update_time_s=3):
        self.last_disk = None
        self.last_net = None
        self.edit_stats_lock = RLock()
        self.update_time_s = update_time_s
        # Finally set the initial stats
        self.stats: Dict[str, Any] = {}

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=self.update_time_s, percpu=True)
        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()
        net_sent_bytes = net.bytes_sent - self.last_net.bytes_sent if self.last_net else 0
        net_recv_bytes = net.bytes_recv - self.last_net.bytes_recv if self.last_net else 0
        disk_read_bytes = disk.read_bytes - self.last_disk.read_bytes if self.last_disk else 0
        disk_write_bytes = disk.write_bytes - self.last_disk.write_bytes if self.last_disk else 0
        self.stats = {
            'memory': psutil.virtual_memory()[2],
            'cpu': {
                'all': cpu,
                'avg': np.average(cpu),
            },
            'disk': {  # MB/s
                'read': (disk_read_bytes / (1024.0 ** 2)) / self.update_time_s,
                'write': (disk_write_bytes / (1024.0 ** 2)) / self.update_time_s,
            },
            'network': {  # MB/s
                'sent': (net_sent_bytes / (1024.0 ** 2)) / self.update_time_s,
                'recv': (net_recv_bytes / (1024.0 ** 2)) / self.update_time_s,
            }
        }
        self.last_net = net
        self.last_disk = disk

    def __getitem__(self, item):
        return self.stats[item]
