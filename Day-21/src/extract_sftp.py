"""SFTP: download an XML file, parse it, land it."""
import os

import paramiko

from src.config import RAW_DIR
from src.formats import xml_to_df
from src.utils import save_raw


def sftp_customers():
    os.makedirs(RAW_DIR, exist_ok=True)
    local_path = f"{RAW_DIR}/customers.xml"

    transport = paramiko.Transport((os.getenv("SFTP_HOST"), int(os.getenv("SFTP_PORT", "22"))))
    transport.connect(username=os.getenv("SFTP_USER"), password=os.getenv("SFTP_PASSWORD"))
    sftp = paramiko.SFTPClient.from_transport(transport)
    try:
        sftp.get(os.getenv("SFTP_REMOTE_PATH"), local_path)
    finally:
        sftp.close()
        transport.close()

    save_raw(xml_to_df(local_path), "sftp_customers", "sftp")
