

class LRUCache(object):
    def __init__(self, func, cap):
        self.cache = {}
        self.last_access_time = {}
        self.time = 0
        self.func = func
        self.lock = threading.Lock()
        self.capacity = cap

    def get(arg):
        self.time += 1
        if arg in self.cache:
            self.last_access_time[arg] = self.time
            val = self.cache[arg]
            return val
        else:
            val = self.func(arg)
            self.cache[arg] = val
            self.last_access_time[arg] = self.time
            return val

    def insert_value():
        pass
