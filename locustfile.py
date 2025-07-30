# https://docs.locust.io/en/stable/quickstart.html#direct-command-line-usage-headless

from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/hello")
        self.client.get("/world")