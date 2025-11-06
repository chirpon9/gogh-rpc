import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def get_log_directory():
    if sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/gogh Japan/gogh/Logs")
    
    elif sys.platform == "win32":
        appdata_path = os.getenv('APPDATA')
        
        if not appdata_path:
            appdata_path = os.path.expanduser("~\\AppData\\LocalLow\\gogh Japan\\gogh\\Logs")
            
        return os.path.join(appdata_path)
        
    else:
        raise NotImplementedError({sys.platform})

DIR = get_log_directory()

def find_newest_log_file(directory):
    newest_file_path = None
    newest_mtime = 0  
    if not os.path.exists(directory):
        return None
    try:
        for filename in os.listdir(directory):
            full_path = os.path.join(directory, filename)
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue
            if mtime > newest_mtime:
                newest_mtime = mtime
                newest_file_path = full_path       
    except Exception as e:
        print(f"Error scanning directory {directory}: {e}")
        return None
    return newest_file_path

class Handler(FileSystemEventHandler): #checks for new log files
    def __init__(self, new_log_callback, log_update_callback):
        super().__init__()
        self.on_new_log_found = new_log_callback
        self.on_log_updated = log_update_callback
        self.current_log_file = None

    def on_created(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        if filename.startswith("NetworkLog_") and filename.endswith(".txt"):
            self.current_log_file = event.src_path
            self.on_new_log_found(self.current_log_file)

    def on_modified(self, event):
        if event.is_directory:
            return
            
        if event.src_path == self.current_log_file:
            self.on_log_updated()

def start_file_watcher(new_log_callback, log_update_callback):
    event_handler = Handler(new_log_callback, log_update_callback)
    existing_log = find_newest_log_file(DIR)
    
    if existing_log:
        event_handler.current_log_file = existing_log
        new_log_callback(existing_log)

    observer = Observer()
    observer.schedule(event_handler, DIR, recursive=False)
    observer.start()

    try:
        print(f"Observer started")
        while True:
            time.sleep(1)
    except FileNotFoundError:
        print("file not found")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        observer.stop()
        observer.join()        