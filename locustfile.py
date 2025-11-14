from locust import HttpUser, task, between, LoadTestShape
import random, os

BASE_URL = os.getenv("BASE_URL", "http://alb-monolito-183015172.us-east-1.elb.amazonaws.com")
GET_PATH = "/orders/"
POST_PATH = "/orders/update/"

class OrdersUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = BASE_URL

    @task(3)  # 60% consultas
    def get_orders(self):
        with self.client.get(GET_PATH, name="GET /orders", catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f"Status {r.status_code}")

    @task(2)  # 40% actualizaciones
    def update_order(self):
        payload = {
            "order_id": random.randint(1, 10000),
            "status": random.choice(["created", "paid", "shipped", "delivered", "cancelled"])
        }
        headers = {"Content-Type": "application/json"}
        with self.client.post(POST_PATH, json=payload, headers=headers, name="POST /orders/update", catch_response=True) as r:
            if r.status_code not in (200, 201, 204):
                r.failure(f"Status {r.status_code}")

class StepLoadShape(LoadTestShape):
    target_users = int(os.getenv("TARGET_USERS", "1200"))
    ramp_seconds = int(os.getenv("RAMP_SECONDS", "120"))
    hold_seconds = int(os.getenv("HOLD_SECONDS", "600"))

    def tick(self):
        run_time = self.get_run_time()
        if run_time < self.ramp_seconds:
            users = int(self.target_users * (run_time / self.ramp_seconds))
            return (max(users, 1), max(users // 10, 1))
        elif run_time < self.ramp_seconds + self.hold_seconds:
            return (self.target_users, max(self.target_users // 10, 1))
        else:
            return None

