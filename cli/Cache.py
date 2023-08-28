class Cache:
    def __init__(self, max_size=10):
        self.cache = {}
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            self.evict()
        self.cache[key] = value

    def evict(self):
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]