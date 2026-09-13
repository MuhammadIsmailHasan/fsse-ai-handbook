from hexajobs.adapters.memory_store import InMemoryJobStore  # 🚩 use cases build their own infrastructure
from hexajobs.domain.model import load_jobs, match_score, notify_matches

STORE = InMemoryJobStore()  # 🚩 global state


def import_jobs(path):
    existing = {job.id for job in STORE.all()}
    new = [job for job in load_jobs(path) if job.id not in existing]
    STORE.save_all(new)
    return len(new)


def recommend_jobs(email, my_skills, stream, threshold=0.5):
    jobs = sorted((j for j in STORE.all() if match_score(j, my_skills) >= threshold), key=lambda j: (-match_score(j, my_skills), j.id))
    if jobs:
        notify_matches(email, jobs, stream)
    return jobs
