import math
import os
import statistics
import time
import datetime 
import random
import sys
import json
import hashlib
import base64
import urllib.request


def _get_list(arr):
    if hasattr(arr, 'elements'):
        return arr.elements
    elif hasattr(arr, 'data'):
        return arr.data
    return arr

def load_module(name):
    if name in STD_MODULES:
        return STD_MODULES[name]
    raise RuntimeError(f"Error : Standard module '{name}' not found")

STD_MODULES = {
    "std::Math": {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "floor": math.floor,
        "ceil": math.ceil,
        "abs": abs,
        "min": min,
        "max": max,
        "PI": math.pi,
        "E": math.e,
    },
    "std::String": {
        "to_upper": lambda s: str(s).upper(),
        "to_lower": lambda s: str(s).lower(),
        "trim": lambda s: str(s).strip(),
        "split": lambda s, delim=" ": str(s).split(delim),
        "join": lambda arr, delim="": delim.join(map(str, _get_list(arr))),
        "replace": lambda s, old, new: str(s).replace(old, new),
        "contains": lambda s, sub: sub in str(s),
        "len": lambda s: len(str(s)),
    },
}

STD_MODULES["std::array"] = {
    "push": lambda arr, val: (_get_list(arr).append(val) or arr),
    "pop": lambda arr: _get_list(arr).pop(),
    "len": lambda arr: len(_get_list(arr)),
    "reverse": lambda arr: list(reversed(_get_list(arr))),
    "slice": lambda arr, start, end=None: _get_list(arr)[start:end],
    "concat": lambda a, b: _get_list(a) + _get_list(b)
}

STD_MODULES["std::file"] = {
    'read': lambda p: open(p, 'r', encoding="utf-8").read(),
    'write': lambda p, c: open(p, 'w', encoding="utf-8").write(str(c)),
    'append': lambda p, c : open(p, 'a', encoding="utf-8").write(str(c)),
    'exists': os.path.exists,
    'remove': os.remove,
    'pwd': os.getcwd,
    'ls': os.listdir,
    'chdir': os.chdir,
}

STD_MODULES["std::stat"] = {
    "mean": lambda arr: sum(_get_list(arr)) / len(_get_list(arr)) if _get_list(arr) else 0,
    "median": lambda arr: statistics.median(_get_list(arr)),
    "mode": lambda arr: statistics.mode(_get_list(arr)),
    "variance": lambda arr: statistics.variance(_get_list(arr)),
    "std_dev": lambda arr: statistics.stdev(_get_list(arr)),
}

STD_MODULES["std::time"] = {
    "now": time.time,
    "sleep": time.sleep,
        "clock": time.perf_counter,
        "format": lambda fmt="%Y-%m-%d %H:%M:%S", ts=None: time.strftime(fmt, time.localtime(ts if ts is not None else time.time())),
        "parse": lambda s, fmt="%Y-%m-%d %H:%M:%S": time.mktime(time.strptime(str(s), fmt)),
        "iso_now": lambda: datetime.datetime.now().isoformat(),
        "year": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).year,
        "month": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).month,
        "day": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).day,
        "hour": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).hour,
        "minute": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).minute,
        "second": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).second,
        "weekday": lambda ts=None: datetime.datetime.fromtimestamp(ts if ts is not None else time.time()).weekday(),
        "add_seconds": lambda ts, secs: ts + secs,
        "add_days": lambda ts, days: ts + (days * 86400),
        "diff_seconds": lambda ts1, ts2: ts1 - ts2,
}

STD_MODULES["std::rand"] = {
    "randint": random.randint,
    "randfloat": random.random,
    "choice": random.choice,
    "shuffle": lambda arr: random.shuffle(_get_list(arr)) or arr,
}

STD_MODULES["std::sys"] = {
    "args": lambda: sys.argv,
    "env": lambda key, default="": os.environ.get(key, default),
    "exit": sys.exit,
    "platform": lambda: sys.platform,
}

STD_MODULES["std::json"] = {
    "parse": json.loads,
    "dump": lambda obj: json.dumps(obj, indent=2),
}

STD_MODULES["std::dict"] = {
    "keys": lambda d: list(d.data.keys()) if hasattr(d, 'data') else list(d.keys()),
    "values": lambda d: list(d.data.values()) if hasattr(d, 'data') else list(d.values()),
    "merge": lambda d1, d2: {**d1, **d2},
}

STD_MODULES["std::crypto"] = {
    "sha256": lambda s: hashlib.sha256(str(s).encode()).hexdigest(),
    "md5": lambda s: hashlib.md5(str(s).encode()).hexdigest(),
    "base64_encode": lambda s: base64.b64encode(str(s).encode()).decode(),
    "base64_decode": lambda s: base64.b64decode(str(s).encode()).decode(),
}

def _http_get(url):
    req = urllib.request.Request(str(url), headers={'User-Agent': 'Veln/1.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

def _http_post(url, data=None):
    body = str(data).encode('utf-8') if data is not None else None
    req = urllib.request.Request(str(url), data=body, headers={'User-Agent': 'Veln/1.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8')

STD_MODULES["std::req"] = {
    "get": _http_get,
    "post": _http_post,
}



# Alias lowercase module names
STD_MODULES["std::math"] = STD_MODULES["std::Math"]
STD_MODULES["std::string"] = STD_MODULES["std::String"]



def debug_inspect(val):
    val_type = type(val).__name__
    if hasattr(val, 'name'):
        val_type = getattr(val, 'name', val_type)
    print(f'[DEBUG INSPECT] Type : {val_type} | value : {val}')
    return val

def debug_typeof(val):
    if isinstance(val, int): return "int"
    if isinstance(val, float): return "float"
    if isinstance(val, str): return "string"
    if isinstance(val, bool): return "bool"
    if hasattr(val, 'name'): return f"struct::{val.name}"
    if hasattr(val, 'elements'): return "array"
    if hasattr(val, 'pairs'): return "hash"
    return type(val).__name__

def debug_trace(msg="checkpoint"):
    """
    Prints a timestamped debug trace message
    """
    now = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"[DEBUG TRACE] {now} ] === {msg} ===")
    return msg


def debug_dump(val):
    """
    Dumps variable as a raw string representation
    """

    return str(val)

timers = {}
def time_start(name="default"):
    timers[name] = time.perf_counter()
    return None

def time_end(name="default"):
    if name in timers:
        elapsed = time.perf_counter() - timers.pop(name)
        print(f"[TIME] {name} : {elapsed:.4f} seconds")
        return elapsed
    return None

STD_MODULES["std::debug"] = {
    "inspect": debug_inspect,
    "typeof": debug_typeof,
    "trace": debug_trace,
    "dump": debug_dump,
    "time_start": time_start,
    "time_end": time_end,
}