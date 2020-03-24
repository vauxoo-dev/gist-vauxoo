from __future__ import print_function

import time
import os
import re

from subprocess import Popen, PIPE, STDOUT

import pysftp
import logging

sftp_download_logger = logging.getLogger()
sftp_download_logger.setLevel('INFO')


version_re = re.compile(r"\d+")

def format_log_progress_mesg(speed, transmitted_bytes, total_transfer_time,
                             is_upload, total_size=None):
    # transmission_type, transmitted = get_transmission_names(is_upload)
    transmission_type = 'download'
    transmitted = 'download'
    eta_string = ''
    if total_size and speed:
        eta = (total_size-transmitted_bytes) / speed
        eta_string = '[ETA: {eta:.1f}s]'.format(eta=eta)
    template = ('Average {transmission_type} speed: {speed:.2f} bytes/sec '
                '(bytes {transmitted}: {transmitted_bytes} of {total_size},'
                ' {transmission_type} elapsed time: {transfer_time:.2f} sec) {eta_string}')
    return template.format(
        speed=speed,
        transmitted_bytes=transmitted_bytes,
        transfer_time=total_transfer_time,
        transmission_type=transmission_type,
        transmitted=transmitted,
        total_size=total_size or 'unknown',
        eta_string=eta_string,
    )

class BaseProgressCallback(object):
    """Base class for building progress log callbacks
    """
    def __init__(self, logger, log_interval=5):
        self.start_ts = time.time()
        self.lastlog_ts = self.start_ts
        self.log_interval = log_interval
        self.logger = logger

    def log_transfer_progress(self, transmitted_bytes, total_size=None, is_upload=False):
        now = time.time()

        total_transfer_time = now - self.start_ts
        speed = float(transmitted_bytes) / total_transfer_time

        reached_log_interval_limit = (now - self.lastlog_ts) > self.log_interval
        if reached_log_interval_limit:
            self.lastlog_ts = now
            print(
                format_log_progress_mesg(speed, transmitted_bytes,
                                         total_transfer_time, is_upload, total_size))


class SftpDownloadProgress(BaseProgressCallback):
    """Progress logging callback for Pysftp's put"""
    def __call__(self, transferred, total_size):
        self.log_transfer_progress(transferred, total_size=total_size)


def progress(transfered, size):
    print("%.2f transfered" % (size/transfered))
    time.sleep(10)

def pysftp_download(host, username, project, localpath):
    with pysftp.Connection(host=host, username=username) as sftp:
        directories = []
        for attr in sftp.listdir_attr():
            dirname = attr.filename
            if not sftp.isdir(dirname) or project.lower() not in dirname.lower():
                continue
            version = version_re.search(dirname)
            version = int(version[0]) if version else 0
            directories.append((version, dirname))
        directories = sorted(directories, reverse=True)
        if not directories:
            return
        directory = directories[0][1]
        sftp.cwd(directory)
        for attr in sftp.listdir_attr():
            if 'auto' in attr.filename.lower() and sftp.isdir(attr.filename):
                sftp.cwd(attr.filename)
                break
        backups = sorted([attr.filename for attr in sftp.listdir_attr() if sftp.isfile(attr.filename)], reverse=True)
        if not backups:
            return
        backup = backups[0]
        backup_path = os.path.join(sftp.getcwd(), backup)
        localpath = os.path.join(localpath, directory, backup)
        if not os.path.isdir(os.path.dirname(localpath)):
            os.makedirs(os.path.dirname(localpath))
        print("sftp '%s' '%s'" % (backup_path, localpath))
        if os.path.isfile(localpath):
            remote_size = sftp.stat(backup_path).st_size
            local_size = os.stat(local_path).st_size
            if abs(remote_size - local_size) <= remote_size*0.10:
                # We don't have the checksum file in the server :(
                print("Skip download file because it was downloaded.")
                continue
        sftp.get(backup_path, localpath=localpath, preserve_mtime=True, callback=SftpDownloadProgress(sftp_download_logger))
