import threading
import time


class DoubleClickManager:
    kDoubleClickTime: float = 0.5
    last_click: float = None
    check_lock = threading.Lock()

    @staticmethod
    def check_double_click():
        with DoubleClickManager.check_lock:
            if DoubleClickManager.last_click is not None:
                elapsed = time.perf_counter() - DoubleClickManager.last_click

                if elapsed <= DoubleClickManager.kDoubleClickTime:
                    DoubleClickManager.last_click = None
                    return True

            DoubleClickManager.last_click = time.perf_counter()
            return False
