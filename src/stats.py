from typing import Any, Dict

import psutil

class DeviceStats:
    def __init__(self, update_time_s=3,
                       net_winsize=20, min_sent=0.1, min_recv=0.1, net_common=0,
                       disk_winsize=2, min_write=0.5, min_read=0.5, disk_common=1):
        self.last_disk = None
        self.last_net = None
        self.update_time_s = update_time_s
        # network attributes
        self.net_winsize = net_winsize
        self.min_sent = min_sent
        self.min_recv = min_recv
        if net_winsize == 0:
            # if winsize is 0, max value is absolute
            self.max_sent = min_sent
            self.max_recv = min_recv
        self.sent_win = [0] * net_winsize
        self.recv_win = [0] * net_winsize
        self.net_common = net_common
        # disk attributes
        self.disk_winsize = disk_winsize
        self.min_write = min_write
        self.min_read = min_read
        if disk_winsize == 0:
            # if winsize is 0, max value is absolute
            self.max_write = min_write
            self.max_read = min_read
        self.write_win = [0] * disk_winsize
        self.read_win = [0] * disk_winsize
        self.disk_common = disk_common
        # Finally set the initial stats
        self.stats: Dict[str, Any] = {}

    def update_stats(self):
        cpu = psutil.cpu_percent(interval=self.update_time_s, percpu=True)
        disk = psutil.disk_io_counters()
        net = psutil.net_io_counters()
        net_sent_bytes = net.bytes_sent - self.last_net.bytes_sent if self.last_net else 0
        net_recv_bytes = net.bytes_recv - self.last_net.bytes_recv if self.last_net else 0
        disk_write_bytes = disk.write_bytes - self.last_disk.write_bytes if self.last_disk else 0
        disk_read_bytes = disk.read_bytes - self.last_disk.read_bytes if self.last_disk else 0
        # In Megabytes
        ns = net_sent_bytes / 1048576 / self.update_time_s  # 1048576 = 1024^2
        nr = net_recv_bytes / 1048576 / self.update_time_s
        dw = disk_write_bytes / 1048576 / self.update_time_s
        dr = disk_read_bytes / 1048576 / self.update_time_s
        # Max values for normalized network stats
        if self.net_winsize == 0:
            self.max_sent = max(self.max_sent, ns)
            self.max_recv = max(self.max_recv, nr)
        else:
            self.sent_win = self.sent_win[1:] + [ns]
            self.recv_win = self.recv_win[1:] + [nr]
            self.max_sent = max(self.sent_win + [self.min_sent])
            self.max_recv = max(self.recv_win + [self.min_recv])
        if self.net_common:
            self.max_sent = max(self.max_sent, self.max_recv)
            self.max_recv = self.max_sent
        # Max values for normalized disk stats
        if self.disk_winsize == 0:
            self.max_read = max(self.max_read, dr)
            self.max_write = max(self.max_write, dw)
        else:
            self.read_win = self.read_win[1:] + [dr]
            self.write_win = self.write_win[1:] + [dw]
            self.max_read = max(self.read_win + [self.min_read])
            self.max_write = max(self.write_win + [self.min_write])
        if self.disk_common:
            self.max_read = max(self.max_read, self.max_write)
            self.max_write = self.max_read
        # print(f'  {self.max_recv:5.2f} ' + ''.join(f'{x:5.2f} ' for x in self.recv_win), end='')
        # print(f'> {self.max_sent:5.2f} ' + ''.join(f'{x:5.2f} ' for x in self.sent_win))
        self.stats = {
            'memory': psutil.virtual_memory()[2],
            'cpu': {
                'all': cpu,
                'avg': sum(cpu) / len(cpu),
            },
            'network': {
                # MB/s
                'raw_sent': ns,
                'raw_recv': nr,
                # %
                'sent': ns * 100 / self.max_sent,
                'recv': nr * 100 / self.max_recv
            },
            'disk': {
                # MB/s
                'raw_write': dw,
                'raw_read': dr,
                # %
                'write': dw * 100 / self.max_write,
                'read': dr * 100 / self.max_read,
            }
        }
        self.last_net = net
        self.last_disk = disk

    def __getitem__(self, item):
        return self.stats[item]
