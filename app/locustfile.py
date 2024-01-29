from locust import HttpUser, task


class WebsiteUser(HttpUser):
    @task
    def list_index_value(self):
        self.client.get("/return_nasdaq_async")

    @task
    def list_index_value2(self):
        self.client.get("/return_nasdaq_sync")
