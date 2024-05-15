# Sync Folder

## Overview

The `sync_folder.py` script is a Python program designed to synchronize the contents of a source directory with a replica directory. It ensures that the replica is an exact copy of the source, adding, updating, or removing files and directories as needed. The program is equipped with features to handle file copying errors, logging, and continuous synchronization with a specified interval.

## Features

1. **MD5 Checksum Calculation**:
    - Calculates the MD5 checksum of files to detect changes and ensure accurate synchronization.

2. **Logging**:
    - Logs detailed information about synchronization operations to both a file and the console.

3. **Path Validation**:
    - Validates user-provided file and directory paths to ensure they exist and are accessible.

4. **User Input Handling**:
    - Prompts users to input the source directory, replica directory, and log file path.
    - Allows users to exit the program gracefully by typing 'q'.

5. **File Copy with Retries**:
    - Attempts to copy files up to three times if an error occurs (e.g., file is open), handling file copying errors gracefully.

6. **Synchronization**:
    - Synchronizes the source directory with the replica directory:
        - Adds or updates files based on MD5 checksum comparison.
        - Creates missing directories in the replica.
        - Removes files and directories from the replica that no longer exist in the source.

7. **Continuous Synchronization Loop**:
    - Runs a continuous synchronization loop with a user-specified interval.
    - Uses threading to run the synchronization concurrently, allowing the program to be stopped gracefully.

8. **Graceful Shutdown**:
    - Handles stopping the synchronization loop on user request or interruption.

## Usage

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/ElMarcio/SyncDir
    cd SyncDir
    ```

2. **Set Up a Virtual Environment (Optional but Recommended)**:
    ```sh
    python -m venv venv
    source venv/bin/activate   # On Windows: venv\Scripts\activate
    ```

3. **Install Required Packages**:
    - Ensure you have Python 3 installed. The script uses standard libraries, so no additional packages are required.

4. **Run the Script**:
    ```sh
    python sync_folder.py
    ```

5. **Provide User Inputs**:
    - When prompted, provide the source directory path, replica directory path, and log file path.
    - Set the synchronization interval in seconds.
    - To exit the program, type 'q' and press Enter.

## Example

```
Insert source folder path: /path/to/source
Insert replica folder path: /path/to/replica
Insert log file path: /path/to/log_file.log
Set up synchronization time (seconds >0): 30
```

## Considerations

- **Threading**: The program uses threading to run the synchronization loop concurrently, ensuring the main program remains responsive.
- **Error Handling**: The program includes robust error handling for file operations, ensuring retries and logging errors appropriately.
- **Logging**: Detailed logs are maintained to track the synchronization process, which is helpful for debugging and monitoring.


## Author

https://github.com/ElMarcio/
