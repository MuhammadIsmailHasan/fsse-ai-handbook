class ConsoleNotifier:
    def __init__(self, stream):
        self.stream = stream

    def notify(self, email, jobs):
        self.stream.write(f"To {email}: {len(jobs)} job(s)\n")
        for job in jobs:
            self.stream.write(f"- {job.title} at {job.company}\n")
