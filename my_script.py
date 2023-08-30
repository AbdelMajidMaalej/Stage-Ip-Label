from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 5)  # Random wait time between 1 and 5 seconds

    @task
    def my_task(self):
        self.client.get("/")  # Simulate a user visiting the homepage