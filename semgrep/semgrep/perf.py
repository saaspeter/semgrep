import json
from datetime import timedelta


class PerfTracker:
    def __init__(self):
        self.events = []
        self.baseline = {}

    def record(self, time: timedelta, rule: str, file: str):
        if self.baseline:
            time = time - timedelta(seconds=self.baseline[rule])
        self.events.append(dict(time=time.total_seconds(), rule=rule, file=file))

    def mark_baseline(self):
        self.baseline = {d['rule']: d['time'] for d in self.events}
        self.events = []

    def dump(self, stream):
        for event in self.events:
            json.dump(event, stream)
            print(file=stream, flush=True)
        self.events = []


Tracker = PerfTracker()
