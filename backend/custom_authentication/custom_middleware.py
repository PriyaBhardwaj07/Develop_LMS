import threading
import time
from django.http import HttpResponseServerError

class TimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define a function to be run in a separate thread
        def process_request():
            # Call the get_response function to handle the request
            self.response = self.get_response(request)

        # Create a thread to execute the request processing function
        request_thread = threading.Thread(target=process_request)
        request_thread.start()
        print('request thread started')

        # Set the timeout threshold (in seconds)
        timeout_threshold = 20

        # Wait for the request processing to finish or until timeout
        request_thread.join(timeout=timeout_threshold)
        print(request_thread)
        print('request thread execution completed')
        # Check if the request processing thread is still alive
        if request_thread.is_alive():
            # If the thread is still alive, it means the request has timed out
            return HttpResponseServerError('Request timed out')

        # If the thread has finished processing, return the captured response
        return self.response
