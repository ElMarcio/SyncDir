import os
import time
import shutil
import logging
import sys
from hashlib import md5
from datetime import datetime
from threading import Thread, Event

"""
KEY NOTES:
- Requests user path for source, replica, log files (if no log, creates new one at given path) and sync timer. 
- MD5 verification for file creation, update, deletion.
- Retry attempts in case of error, else continue
- Relevant data recorded in log and displayed in terminal
- User input to close program 'q'
"""


def calculate_md5(file_path):
    """Calculate the MD5 checksum of a file."""
    try:
        hash_md5 = md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        logging.error(f"Unable to access file for MD5 calculation: {file_path}. Error: {e}")
        return None


def setup_logger(log_file):
    """Setup logging configuration to log to both file and console."""
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    # Create file handler which logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def validate_path(path, type_of_path):
    """Validate the provided file path."""
    if type_of_path == "file":
        if not os.path.isfile(path):
            return False
    elif type_of_path == "dir":
        if not os.path.isdir(path):
            return False
    return True


def get_input(prompt, type_of_path):
    """Get user input and validate path or ensure log file can be created."""
    while True:
        path = input(prompt)
        if path.lower() == 'q':
            print("Exiting program...")
            sys.exit(0)
        if type_of_path == "file":
            # Try to open the file in append mode, which will create the file if it doesn't exist
            try:
                with open(path, 'a'):
                    pass
                return path
            except IOError:
                print("File doesn't exist or wrong type of file.")
        elif validate_path(path, type_of_path):
            return path
        else:
            print("Path inserted doesn't exist or wrong type of file.")


def copy_file_with_retries(src, dst, max_retries=3, delay=2):
    """Attempt to copy a file with retries on IOError."""
    for attempt in range(1, max_retries + 1):
        try:
            shutil.copy2(src, dst)
            return True
        except IOError as e:
            logging.warning(f"Attempt {attempt} failed: Could not copy {src} to {dst}. Error: {e}")
            time.sleep(delay)
    logging.error(f"Failed to copy {src} to {dst} after {max_retries} attempts.")
    return False


def perform_sync(source, replica, logger):
    """Synchronize the source directory to the replica directory and log changes."""
    changes = False
    source_files = set()
    replica_files = set()

    # Walk through source directory and update/add files in the replica
    for src_dir, _, files in os.walk(source):
        dst_dir = src_dir.replace(source, replica, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
            logger.info(f"Directory created: {dst_dir}")

        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            source_files.add(src_file)
            replica_files.add(dst_file)

            # Check if the destination file exists and compare MD5 checksums
            if not os.path.exists(dst_file):
                if copy_file_with_retries(src_file, dst_file):
                    logger.info(f"Created file: {dst_file}")
                    changes = True
            elif calculate_md5(src_file) != calculate_md5(dst_file):
                if copy_file_with_retries(src_file, dst_file):
                    logger.info(f"Updated file: {dst_file}")
                    changes = True

    # Remove extra files and directories in the replica that do not exist in the source
    for dst_dir, _, files in os.walk(replica, topdown=False):  # topdown=False to handle from deepest to shallowest
        src_dir = dst_dir.replace(replica, source, 1)
        for file_ in files:
            dst_file = os.path.join(dst_dir, file_)
            src_file = os.path.join(src_dir, file_)
            if src_file not in source_files:
                try:
                    os.remove(dst_file)
                    logger.info(f"Deleted file: {dst_file}")
                    changes = True
                except IOError as e:
                    logger.error(f"Failed to delete {dst_file}. Error: {e}")
        # Remove extra directories
        if not os.path.exists(src_dir):
            os.rmdir(dst_dir)
            logger.info(f"Deleted directory: {dst_dir}")
            changes = True

    return changes


def sync_loop(source, replica, interval, logger, stop_event):
    """Continuous synchronization loop that can be stopped by an event."""
    try:
        while not stop_event.is_set():
            print(f"{datetime.now()} Syncing...")
            if perform_sync(source, replica, logger):
                print(f"{datetime.now()} Sync completed with changes.")
            else:
                print(f"{datetime.now()} No updates.")
            stop_event.wait(interval)
    except KeyboardInterrupt:
        print("Program exited by user.")
    finally:
        print("Synchronization stopped.")


def main():
    print("To close the program, simply exit or type 'q'")
    source = get_input("Insert source folder path: ", "dir")
    replica = get_input("Insert replica folder path: ", "dir")
    log_file = get_input("Insert log file path (if non-existent, creates a new one): ", "file")
    setup_logger(log_file)
    interval = int(input("Set up synchronization time (seconds >0): "))
    logger = logging.getLogger('')

    # Create an event to signal the sync thread to stop
    stop_event = Event()

    sync_thread = Thread(target=sync_loop, args=(source, replica, interval, logger, stop_event))
    sync_thread.start()

    while True:
        user_input = input("").lower()
        if user_input == 'q':
            stop_event.set()  # Signal the thread to stop
            break

    sync_thread.join()
    print("Program has exited.")


if __name__ == "__main__":
    main()
