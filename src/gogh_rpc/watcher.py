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
    def __init__(self, new_log_callback, log_update_callback, game_closed_callback):
        super().__init__()
        self.on_new_log_found = new_log_callback
        self.on_log_updated = log_update_callback
        self.on_game_closed = game_closed_callback
        self.current_log_file = None
        self.last_modified_time = time.time()

    def on_created(self, event):
        if event.is_directory:
            return

        filename = os.path.basename(event.src_path)
        if filename.startswith("NetworkLog_") and filename.endswith(".txt"):
            self.current_log_file = event.src_path
            self.last_modified_time = time.time()
            self.on_new_log_found(self.current_log_file)

    def on_modified(self, event):
        if event.is_directory:
            return
            
        if event.src_path == self.current_log_file:
            self.last_modified_time = time.time()
            self.on_log_updated()
    
    def check_for_timeout(self, timeout_seconds):
        if self.current_log_file and (time.time() - self.last_modified_time) > timeout_seconds:
            return True
        return False

def start_file_watcher(new_log_callback, log_update_callback, game_closed_callback=None, timeout_seconds=60):
    event_handler = Handler(new_log_callback, log_update_callback, game_closed_callback)
    existing_log = find_newest_log_file(DIR)
    
    if existing_log:
        event_handler.current_log_file = existing_log
        event_handler.last_modified_time = time.time()
        new_log_callback(existing_log)

    observer = Observer()
    observer.schedule(event_handler, DIR, recursive=False)
    observer.start()

    try:
        print(f"Observer started, monitoring for game activity (timeout: {timeout_seconds}s)")
        while True:
            time.sleep(1)
            
            # Check if the game has been inactive for too long
            if game_closed_callback and event_handler.check_for_timeout(timeout_seconds):
                print(f"No log activity for {timeout_seconds} seconds, game appears to be closed")
                game_closed_callback()
                break
                
    except FileNotFoundError:
        print("file not found")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        observer.stop()
        observer.join()        