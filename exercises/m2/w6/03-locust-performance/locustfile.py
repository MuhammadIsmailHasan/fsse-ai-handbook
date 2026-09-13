"""YOUR load test for target_app.py. See README.md for the requirements.

Run with the web UI:   uv run locust -f m2/w6/03-locust-performance/locustfile.py --host http://127.0.0.1:5092
"""

from locust import HttpUser, between, task

API = "/api/v1"


class JobSeeker(HttpUser):
    wait_time = between(1, 3)

    # TODO on_start: log in once and remember an Authorization header

    @task
    def browse_jobs(self):
        # TODO weight 5, detect "degraded" 200 responses with catch_response, name="GET /api/v1/jobs"
        self.client.get(f"{API}/jobs")

    # TODO view_job   (weight 3): GET /api/v1/jobs/<random 1..50>, grouped as "GET /api/v1/jobs/[id]"
    # TODO save_job   (weight 1): POST /api/v1/jobs/<random 1..50>/save with the token, grouped as "POST /api/v1/jobs/[id]/save"
