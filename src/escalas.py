from random import betavariate as b, seed

from typing import Any, Dict

import psutil

from math import log2


seed(33)




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


stats = DeviceStats()
# print(stats.stats)
# cpu_usage = [max((usage / 100) * 14, 1) for usage in stats['cpu']['all']]
nMuestras = 2
lastValues = [1] * nMuestras
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
    m = max(lastValues + [0.5])
    hr = int(dr / m * 16)
    hw = int(dw / m * 16)
    print(f"{hr:2d} {hw:2d} {m:7.2f} {raw_dr:7.2f} {raw_dw:7.2f} ", end='')
    print('*' * hr + '.' * (16 - hr) + ' ' + '*' * hw + '.' * (16 - hw))
quit()



a = []
for i in range(100):
    a.append(int((500*b(0.5, 0.5))))

hmax = 0    # Altura máxima de las últimas 'nMuestras'
nMuestras = 10
lastValues = [0] * nMuestras
for v in a:
    if v > hmax:
        hmax = v
    h = int(v * 16.0 / hmax)
    # print(h)
    print('*' * h)

