class InMemoryJobStore:
    def __init__(self):
        self._jobs = []

    def save_all(self, jobs):
        self._jobs.extend(jobs)

    def all(self):
        return list(self._jobs)
