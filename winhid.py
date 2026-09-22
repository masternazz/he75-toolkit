"""Windows hid.dll transport for the vendored epomaker_driver (which is Linux/hidraw only).
Only the two calls Transport uses on USB: set_feature(65 bytes) and get_feature(0, 64)."""
import ctypes, subprocess, sys, time, types
from ctypes import wintypes

sys.modules.setdefault("fcntl", types.ModuleType("fcntl"))   # transport.py imports it; unused on this path
sys.path.insert(0, __import__("os").path.join(__import__("os").path.dirname(__file__), "vendor"))

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
hid = ctypes.WinDLL("hid", use_last_error=True)
k32.CreateFileW.restype = wintypes.HANDLE
k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
hid.HidD_SetFeature.argtypes = hid.HidD_GetFeature.argtypes = [wintypes.HANDLE, ctypes.c_char_p, wintypes.ULONG]


def find_path(vid=0x3151, pid=0x5054, mi="MI_02"):
    """Device path of the vendor command interface, built from its PnP instance id."""
    bs = chr(92)   # backslash, spelled out so nothing can mangle it
    prefix = f"HID{bs}VID_{vid:04X}&PID_{pid:04X}&{mi}"
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
        f"(Get-PnpDevice -PresentOnly | Where-Object InstanceId -like '{prefix}*').InstanceId"],
        capture_output=True, text=True).stdout.strip()
    if not out:
        raise RuntimeError("keyboard not found (USB cable in?)")
    return bs * 2 + "?" + bs + out.replace(bs, "#") + "#{4d1e55b2-f16f-11cf-88cb-001111000030}"


class WinHidIO:
    def __init__(self, path):
        self.h = k32.CreateFileW(path, 0xC0000000, 3, None, 3, 0, None)
        if self.h in (None, ctypes.c_void_p(-1).value):
            raise OSError(f"cannot open {path} (close the EPOMAKER driver app)")

    def close(self):
        k32.CloseHandle(self.h)

    def set_feature(self, data):
        self.last = bytes(data)[1:]
        if not hid.HidD_SetFeature(self.h, bytes(data), len(data)):
            raise OSError(f"SetFeature failed: {ctypes.get_last_error()}")

    def get_feature(self, report_id, size):
        # Windows hands back an echo of our own request until the board has answered; retry past it.
        time.sleep(0.03)   # give the board time to answer, or we can read the previous page's reply
        for _ in range(15):
            buf = ctypes.create_string_buffer(bytes([report_id]) + bytes(size))
            if not hid.HidD_GetFeature(self.h, buf, size + 1):
                raise OSError(f"GetFeature failed: {ctypes.get_last_error()}")
            data = buf.raw[1:size + 1]
            if data != getattr(self, "last", None):
                return data
            time.sleep(0.01)
        return data   # no distinct reply (e.g. the wireless-dongle version query with no dongle): echo is the answer


def open_keyboard(pid=0x5054):
    from epomaker_driver.transport import Transport
    from epomaker_driver.he import HEKeyboard
    return HEKeyboard(Transport(WinHidIO(find_path(pid=pid)), "usb"), product_id=pid)
