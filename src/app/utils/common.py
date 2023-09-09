import threading

# Create a global dictionary to store stop flags for each camera
stop_flags = {}
# Create a lock for thread-safe access to the stop flags
stop_flags_lock = threading.Lock()
