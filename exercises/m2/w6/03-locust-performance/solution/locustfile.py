"""Load test for the job board: a job seeker who browses a lot and saves occasionally.

Run with the web UI:   uv run locust -f m2/w6/03-locust-performance/locustfile.py --host http://127.0.0.1:5092
Headless:              uv run locust -f ... --host ... --headless -u 20 -r 5 -t 1m --csv results
"""

import random

from locust import HttpUser, between, task

API = "/api/v1"


class JobSeeker(HttpUser):
    wait_time = between(1, 3)  # "think time" between actions, like a real person

    def on_start(self):
        # Runs once per simulated user: log in and keep the token.
        response = self.client.post(f"{API}/login", json={"email": "seeker@example.com", "password": "load-test"}, name="POST /api/v1/login")
        self.headers = {"Authorization": f"Bearer {response.json()['token']}"}

    @task(5)
    def browse_jobs(self):
        with self.client.get(f"{API}/jobs", name="GET /api/v1/jobs", catch_response=True) as response:
            # A 200 with an error body is still a failure for the user.
            if response.status_code != 200 or "data" not in response.json():
                response.failure("degraded response")

    @task(3)
    def view_job(self):
        job_id = random.randint(1, 50)
        # name= groups /jobs/1, /jobs/2, … into ONE row in the statistics.
        self.client.get(f"{API}/jobs/{job_id}", name="GET /api/v1/jobs/[id]")

    @task(1)
    def save_job(self):
        job_id = random.randint(1, 50)
        self.client.post(f"{API}/jobs/{job_id}/save", headers=self.headers, name="POST /api/v1/jobs/[id]/save")
