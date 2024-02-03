from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)
    host = "http://127.0.0.1:8000"

    @task(1)
    def return_index_async(self):
        self.client.get("/return_index_data?collection_name=NASDAQ")

    @task(1)
    def return_index_sync(self):
        self.client.get("/return_index_data_sync?collection_name=NASDAQ")

    # @task
    # def add_stock_data_async(self):
    #     self.client.post("/add_stock_data_async", json={"file_name": "stocks/AMZN.json"})
    #
    # @task
    # def add_stock_data_sync(self):
    #     self.client.post("/add_stock_data_sync", json={"file_name": "stocks/AMZN.json"})