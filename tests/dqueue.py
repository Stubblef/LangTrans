import queue
import asyncio

class AsyncDataQueue:
    def __init__(self, data_list):
        self.queue = asyncio.Queue()
        for item in data_list:
            self.queue.put_nowait(item)
        self.length = len(data_list)

    async def get_next(self, num_items=1):
        items = []
        for _ in range(num_items):
            try:
                items.append(self.queue.get_nowait())
                self.queue.task_done()
            except asyncio.QueueEmpty:
                break
        return items if items else None

    async def add_data(self, data):
        await self.queue.put(data)
        self.length += 1

    async def put(self, data):
        await self.queue.put(data)
        self.length += 1

    def qsize(self):
        return self.queue.qsize()
    
    def empty(self):
        return self.queue.empty()
    
    async def get_all(self):
        items = []
        while not self.queue.empty():
            items.append(self.queue.get_nowait())
            self.queue.task_done()
        return items
    
    def clear(self):
        while not self.queue.empty():
            self.queue.get_nowait()
            self.queue.task_done()
        self.length = 0
        

class DataQueue:
    def __init__(self, data_list):
        self.queue = queue.Queue()
        for item in data_list:
            self.queue.put(item)
        self.length = len(data_list)

    def get_next(self, num_items=1):
        items = []
        for _ in range(num_items):
            try:
                items.append(self.queue.get_nowait())

            except queue.Empty:
                break
        return items if items else None

    def add_data(self, data):
        self.queue.put(data)
        self.length += 1
        
    
    def put(self, data):
        self.queue.put(data)
        self.length += 1

    def qsize(self):
        return self.queue.qsize()
    
    def empty(self):
        return self.queue.empty()
    
    def get_all(self):
        return list(self.queue.queue)
    
    def clear(self):
        self.queue.queue.clear()
        self.length = 0