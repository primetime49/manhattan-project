import subprocess

class Queue:
    def __init__(self,max_n):
        self.max_n = max_n
        self.queue = []
    
    def append_queue(self, filename):
        self.queue.append(filename)

    def compute_workload(self, filename):
        with open(filename) as f:
            lines = f.readlines()
            return len(lines)

    def queue_job(self):
        filename = self.queue.pop()
        out = subprocess.run(['firejail', 'touch', filename], capture_output=True, text=True)
        return(out.stdout+' ; '+str(self.compute_workload(filename)))
