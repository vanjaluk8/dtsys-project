from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2.5)
    host = "http://127.0.0.1:8000"

    @task
    def fetch_stock_price(self): # Define a task to fetch stock price data for a specific symbol
        symbol = "AMZN"
        start_date = "2023-01-01"
        end_date = "2024-01-01"

        # Define the URL with parameters
        url = f"/stock_price/{symbol}?start_date={start_date}&end_date={end_date}"

        # Make a GET request to the specified URL
        self.client.get(url)

    @task
    def fetch_stock_info(self): # Define a task to fetch stock info for a specific symbol
        symbol = "AMZN"
        self.client.get(f"/stock_info/{symbol}")


# RUN LOCUST FOR LOAD TESTING
# loucst -f locustfile.py