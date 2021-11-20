""" Network and disk bars test """

import psutil
from math import log2
from typing import Any, Dict

class DeviceStats:
    def __init__(self, update_time_s=3):
        self.last_disk = None
        self.last_net = None
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
                'avg': sum(cpu) / len(cpu)
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



def DiskUsage(stats):
    nMuestras = 2
    top_min = 0.1
    lastValues = [0] * nMuestras
    while True:
        stats.update_stats()
        # print(stats['cpu']['avg'])
        raw_dr = stats['disk']['read']
        raw_dw = stats['disk']['write']
        # dr = log2(1 + raw_dr)
        # dw = log2(1 + raw_dw)
        dr = raw_dr
        dw = raw_dw
        lastValues = lastValues[1:] + [max(dr, dw)]
        top_max = max(lastValues + [top_min])
        hr = int(dr / top_max * 16)
        hw = int(dw / top_max * 16)
        print(f"{hr:2d} {hw:2d} {top_max:7.2f} {raw_dr:7.2f} {raw_dw:7.2f} ", end='')
        print('*' * hr + '.' * (16 - hr) + ' ' + '*' * hw + '.' * (16 - hw))

def NetworkUsage(stats, win_size=10, min_sent=0.1, min_recv=0.1):
    """ win_size = 0  => max is absolute """
    if win_size == 0:
        max_sent = min_sent
        max_recv = min_recv
    sent_win = [0] * win_size
    recv_win = [0] * win_size
    while True:
        stats.update_stats()
        ns = stats['network']['sent']
        nr = stats['network']['recv']
        if win_size == 0:
            max_sent = max(max_sent, ns)
            max_recv = max(max_recv, nr)
        else:
            sent_win = sent_win[1:] + [ns]
            recv_win = recv_win[1:] + [nr]
            max_sent = max(sent_win + [min_sent])
            max_recv = max(recv_win + [min_recv])
        hs = int(ns / max_sent * 16)
        hr = int(nr / max_recv * 16)
        print(f"{hs:2d} {hr:2d} {max_sent:7.2f} {max_recv:7.2f} {ns:7.2f} {nr:7.2f} ", end='')
        print('*' * hs + '.' * (16 - hs) + ' ' + '*' * hr + '.' * (16 - hr))

DiskUsage(DeviceStats())
# NetworkUsage(DeviceStats(), 10)
