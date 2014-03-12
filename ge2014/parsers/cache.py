import logging
import json
import os
import functools
import inspect
import csv
from cStringIO import StringIO

logger = logging.getLogger("base")

def to_kwargs(f, *args, **kwargs):
    """Takes arguments given to a function and converts all of them into keyword arguments by looking at the function signature.
    
    >>> def f(a, b=2): pass
    ...
    >>> to_kwargs(f, 1)
    {'a': 1, 'b': 2}
    >>> to_kwargs(f, 1, 3)
    {'a': 1, 'b': 3}
    >>> to_kwargs(f, b=3, a=1)
    {'a': 1, 'b': 3}
    """

    s = inspect.getargspec(f)
    defaults = s.defaults or []
    default_args = s.args[-len(defaults):]

    kw = {}
    kw.update(zip(default_args, defaults))
    kw.update(kwargs)
    kw.update(zip(s.args, args))
    return kw

def to_args(f, *args, **kwargs):
    """Takes arguments given to a function and converts all of them into
    positional arguments by looking at the function signature.

    >>> def f(a, b=2): pass
    ...
    >>> to_args(f, 1)
    [1, 2]
    >>> to_args(f, 1, 3)
    [1, 3]
    >>> to_args(f, b=3, a=1)
    [1, 3]
    """
    kwargs = to_kwargs(f, *args, **kwargs)
    s = inspect.getargspec(f)
    return [kwargs[a] for a in s.args]

def disk_memoize(path):
    """Returns a decorator to cache the function return value in the specified file path.

    If the path ends with .json, the return value is encoded into JSON before saving and decoded on read.
    
    String formatting opeator can be used in the path, the actual path is constructed by formatting the specified path using the argument values.
    
    Usage:
    
        @disk_memoize("data/c_{number:02d}")
        def get_consititency(self, number):
            ...

        @disk_memoize("data/c_{1:02d}")
        def get_consititency(self, number):
            ...

    """
    def decorator(f):
        @functools.wraps(f)
        def g(*a, **kw):
            kwargs = to_kwargs(f, *a, **kw)
            args = to_args(f, *a, **kw)
            filepath = path.format(*args, **kwargs)            
            disk = Disk()
            content = disk.read(filepath)
            if content:
                return content
            else:
                content = f(*a, **kw)
                content = disk.write(filepath, content)
                return disk.read(filepath)
        return g
    return decorator

def safestr(x):
    if isinstance(x, (list, set)):
        return [safestr(a) for a in x]
    if isinstance(x, unicode):
        return x.encode('utf-8')
    else:
        return x

class Disk:
    """Simple wrapper to read and write files in various formats.
    
    This takes care of coverting the data to and from the required format. The default format is text.

    Other supported formats are:
        * json
    """
    def write(self, path, content):
        if path.endswith(".json"):
            if inspect.isgenerator(content):
                content = list(content)
            content = json.dumps(content, indent=4)
        elif path.endswith(".csv"):
            f = StringIO()
            w = csv.writer(f)
            w.writerows([safestr(row) for row in content])
            content = f.getvalue()
        elif path.endswith(".tsv"):
            f = StringIO()
            w = csv.writer(f, delimiter="\t")
            w.writerows([safestr(row) for row in content])
            content = f.getvalue()
            
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        logger.info("saving %s", path)
        with open(path, 'w') as f:
            f.write(content)
    
    def read(self, path):
        if os.path.exists(path):
            logger.info("reading %s", path)
            f = open(path)
            if path.endswith(".json"):
                return json.load(f)
            elif path.endswith(".csv"):
                reader = csv.reader(f)
                return list(reader)
            elif path.endswith(".tsv"):
                reader = csv.reader(f, delimiter="\t")
                return list(reader)
            else:
                return f.read()
            
def setup_logger():            
    FORMAT = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)
