import os

DATA_DIR = os.getenv("DATA_DIR", "./data")
RAW_DIR = f"{DATA_DIR}/raw"
FILES_DIR = f"{DATA_DIR}/files"
CONVERTED_DIR = f"{DATA_DIR}/converted"
SFTP_LOCAL_DIR = os.getenv("SFTP_LOCAL_DIR", "./sftp_data")
