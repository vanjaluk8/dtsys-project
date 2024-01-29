import requests
import time

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time} seconds to execute.")
        return result
    return wrapper


@timer_decorator
def simple_request():
    response = requests.get("http://localhost:8000/list_index_value")
    return response.json()


print(simple_request())