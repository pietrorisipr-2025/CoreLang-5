import time, random, heapq
from collections import deque
class ShardTask: 
    __slots__=("prio","cat","url","retry","next_ts")
    def __init__(self, prio, cat, url): self.prio=prio; self.cat=cat; self.url=url; self.retry=0; self.next_ts=0
class Scheduler:
    def __init__(self, K:int): self.K=K; self.queues={}; self.heap=[]
    def add(self, cat, url, prio=0):
        self.queues.setdefault(cat, deque()).append(ShardTask(prio,cat,url))
    def _pop_rr(self):
        for c in sorted(self.queues.keys()):
            q=self.queues[c]
            if q:
                best=min(range(len(q)), key=lambda i:q[i].prio); t=q[best]; del q[best]; return t
        return None
    def _schedule_retry(self, t):
        t.retry+=1; backoff=min(2**t.retry,60); jitter=random.uniform(0,0.25*backoff); t.next_ts=time.time()+backoff+jitter
        heapq.heappush(self.heap,(t.next_ts,t))
    def next_batch(self):
        now=time.time()
        while self.heap and self.heap[0][0]<=now:
            _,t=heapq.heappop(self.heap); self.queues.setdefault(t.cat, deque()).appendleft(t)
        batch=[]; 
        while len(batch)<self.K:
            t=self._pop_rr()
            if not t: break
            batch.append(t)
        return batch
    def feedback(self, task, ok:bool):
        if not ok: self._schedule_retry(task)
