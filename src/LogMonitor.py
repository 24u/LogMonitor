#!/usr/local/bin/python3

# version 1.0.3.0

import json
import copy
import os
import re
import http.client
import urllib
import smtplib
import sys
import logging.handlers
from email.mime.text import MIMEText
from email.utils import formatdate
from email.utils import make_msgid

XMAILER_NAME = "LogMonitor 1.0"

root = os.path.dirname(sys.argv[0])
CONFIG_FILE_PATH = os.path.join(root, "LogMonitorConfig.txt")
LAST_LINES_FILE_PATH = os.path.join(root, "LastLinesLogs.txt")
LOG_FILE_PATH = os.path.join(root, "LogMonitor.log")

MAX_MBODY_SIZE = 500000
MAX_LOGGING_SIZE = 5000000


class EmailClient(object):
    def __init__(self, server, port, login, password, use_tls, sender, recipient):
        self._server = server
        self._port = port
        self._login = login
        self._password = password
        self._use_tls = use_tls
        self._sender = sender
        self._recipient = recipient

    def send_email(self, subject, message):
        sender = self._sender
        recipient = self._recipient

        msg = MIMEText(message)
        msg['From'] = sender
        msg['To'] = recipient
        msg['Date'] = formatdate(localtime=True)
        msg['Message-id'] = make_msgid()
        msg['Subject'] = subject
        msg["X-Mailer"] = XMAILER_NAME

        try:
            smtp = smtplib.SMTP(self._server, self._port, timeout=30)
            if self._use_tls:
                smtp.starttls()
            if self._login and self._password:
                smtp.login(str(self._login), str(self._password))
            smtp.sendmail(sender, [recipient], msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            my_logger.error("Can't send an email notification. Error: {0}.".format(str(e)))
            return False


class cMail:
    def __init__(self):
        self.host = ""
        self.port = 587
        self.user = ""
        self.password = ""
        self.sender = ""
        self.recipient = ""
        self.subject = ""
        self.mbody = ""
        self.useTls = False


class cNotification:
    def __init__(self):
        self.host = ""
        self.path = ""
        self.appToken = ""
        self.userKey = ""
        self.priority = ""
        self.title = ""
        self.nbody = ""


class cDataset:
    def __init__(self):
        self.filePath = ""
        self.fileRegex = ""
        self.regexRow = ""
        self.allowPushNotification = ""
        self.emailSubject = ""


class Offsets:
    def __init__(self):
        self.offsets = self.load()

    @staticmethod
    def load():
        with open(LAST_LINES_FILE_PATH, encoding="utf-8") as offsets_file:
            return json.load(offsets_file)

    def prepare_offsets(self, files_dict):
        keys = self.offsets.keys()

        newOffsets = copy.deepcopy(self)

        for key in keys:
            row_offset = self.get_row(key)
            if row_offset != 0:
                for file in files_dict:
                    if len(files_dict[file]) >= row_offset:
                        last_line = self.get_last_line(key)
                        try:
                            if files_dict[file][row_offset] == last_line:
                                if file != key:
                                    newOffsets.update(file, row_offset, last_line)
                                    newOffsets.update(key, 0, "")
                        except:
                            print("Out of index")
                            print("Dataset:")
                            print(file)

        for file in files_dict:
            if file not in newOffsets.offsets:
                newOffsets.update(file, 0, "")

        self.offsets = newOffsets.offsets

    def save(self):
        with open(LAST_LINES_FILE_PATH, 'w', encoding="utf-8") as offsets_file:
            json.dump(self.offsets, offsets_file)

    def get_row(self, file_path):
        if file_path in self.offsets:
            return self.offsets[file_path]["offset"]
        return None

    def get_size(self, file_path):
        if file_path in self.offsets:
            return self.offsets[file_path]["size"]
        return None

    def get_last_line(self, file_path):
        if file_path in self.offsets:
            return self.offsets[file_path]["last_line"]
        return None

    def update(self, file_path, offset, last_line, report=False):
        if report:
            if self.get_row(file_path) != offset and self.get_last_line(file_path) != last_line:
                 print("updating {}".format(file_path))

        if file_path in self.offsets:
            self.offsets[file_path]["offset"] = offset
            self.offsets[file_path]["last_line"] = last_line
        else:
            self.offsets[file_path] = {"offset": offset, "last_line": last_line}

    def remove_old_and_save(self, current_files):
        keys = self.offsets.keys()
        for key in list(keys):
            if key not in current_files:
                del self.offsets[key]

        self.save()


class cLogMonitor:
    def __init__(self, config_file_path):
        self.mail = cMail()
        self.notification = cNotification()
        self.datasets = []
        self.offsets = Offsets()
        self.processed_files = []
        self.read_and_parse_config_file(config_file_path)

    def read_and_parse_config_file(self, config_file_path):
        try:
            with open(config_file_path, "r", encoding="utf-8") as config_file:
                config = json.loads(config_file.read())
                self.mail.host = config["notification"]["mail"]["host"]
                if 'port' in config["notification"]["mail"]:
                    self.mail.port = config["notification"]["mail"]["port"]
                self.mail.user = config["notification"]["mail"]["user"]
                self.mail.password = config["notification"]["mail"]["password"]
                self.mail.sender = config["notification"]["mail"]["from"]
                self.mail.recipient = config["notification"]["mail"]["to"]
                if 'use_tls' in config["notification"]["mail"]:
                    self.mail.useTls = config["notification"]["mail"]["use_tls"]
                self.notification.host = config["notification"]["push_notification"]["host"]
                self.notification.path = config["notification"]["push_notification"]["path"]
                self.notification.appToken = config["notification"]["push_notification"]["app_token"]
                self.notification.userKey = config["notification"]["push_notification"]["user_key"]
                self.notification.priority = config["notification"]["push_notification"]["priority"]

                for dataset in config["datasets"]:
                    newDataset = cDataset()
                    newDataset.filePath = dataset["file_path"]
                    newDataset.fileRegex = dataset["file_regex"]
                    newDataset.regexRow = dataset["regex_row"]
                    newDataset.allowPushNotification = dataset["send_pushnotification"]

                    if len(dataset["subject"]) > 70:
                        newDataset.emailSubject = dataset["subject"][:70]
                    else:
                        newDataset.emailSubject = dataset["subject"]

                    self.datasets.append(newDataset)
        except:
            my_logger.error("couldn't process config file")

    def processFiles(self, files, dataset):

        try:
            pattern = re.compile(dataset.regexRow)
        except:
            my_logger.error("cannot parse regular expression in regex_row: " + dataset.regexRow)

        offsets_to_update = {}

        isDatasetStart = True
        datasetStartText = "Starting dataset: \"" + dataset.emailSubject + "\"" + os.linesep + os.linesep
        isDatasetSuccesful = False
        datasetEndText = os.linesep + "Ending dataset: \"" + dataset.emailSubject + "\"" + os.linesep + os.linesep

        for fileName in files:
            lines = files[fileName]

            offset = self.offsets.get_row(fileName)
            if offset != 0:
                offset += 1

            for lineNumber in range(offset, len(lines)):

                if pattern.match(lines[lineNumber]):

                    if isDatasetStart:
                        if len(self.mail.mbody) + len(datasetStartText) <= MAX_MBODY_SIZE:
                            self.mail.mbody += datasetStartText
                            isDatasetSuccesful = True
                            isDatasetStart = False

                    if self.mail.subject == "":
                        self.mail.subject = dataset.emailSubject
                    if len(self.mail.mbody) + len(lines[lineNumber]) <= MAX_MBODY_SIZE:
                        self.mail.mbody += lines[lineNumber]

                    if dataset.allowPushNotification == "yes":
                        if len(self.notification.nbody) + len(lines[lineNumber]) <= 1024:
                            self.notification.nbody += lines[lineNumber]
                        if self.notification.title == "":
                            self.notification.title = dataset.emailSubject

                offset = lineNumber

            if len(lines) > offset:
                offsets_to_update[fileName] = {"offset": offset, "last_line": lines[offset]}
                #: self.offsets.update(fileName, offset, lines[offset])

            # add a new line after every dataset
            if isDatasetSuccesful:
                self.mail.mbody += os.linesep

            if len(self.notification.nbody) > 0:
                self.notification.nbody += os.linesep

        if isDatasetSuccesful:
            self.mail.mbody += datasetEndText + os.linesep

        return offsets_to_update

    def processDatasets(self):
        offsets_to_update = {}
        for dataset in self.datasets:
            files = {}
            try:
                pattern = re.compile(dataset.fileRegex)
            except:
                my_logger.error("cannot parse regular expression in file_path: " + dataset.fileRegex)
            try:
                filePaths = os.listdir(dataset.filePath)
            except:
                my_logger.error("cannot open path: " + dataset.filePath)
                continue

            for filepath in filePaths:
                if pattern.match(filepath) is not None:
                    with open(os.path.join(dataset.filePath, filepath), encoding="utf-8") as file:
                        self.processed_files.append(os.path.join(dataset.filePath, filepath))
                        files[os.path.join(dataset.filePath, filepath)] = file.readlines()
            self.offsets.prepare_offsets(files)
            tmp_offsets = self.processFiles(files, dataset)
            for offset in tmp_offsets:
                offsets_to_update[offset] = tmp_offsets[offset]

        for offset in offsets_to_update:
            self.offsets.update(offset, offsets_to_update[offset]["offset"], offsets_to_update[offset]["last_line"])


def get_platform_eol():
    import sys
    if sys.platform == 'win32':
        return "\r\n"
    else:
        return "\n"

def send_pushnotification(text, host, path, token, key, priority, title):
    conn = http.client.HTTPConnection(host)
    conn.request("POST", path,
                 urllib.parse.urlencode({
                     "token": token,
                     "user": key,
                     "message": text,
                     "priority": priority,
                     "title": title,
                 }), {"Content-type": "application/x-www-form-urlencoded"})

    res = conn.getresponse()
    return res


if __name__ == "__main__":

    # Set up a specific logger with our desired output level
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.DEBUG)

    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=MAX_LOGGING_SIZE, backupCount=1)

    formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)

    my_logger.addHandler(handler)

    try:
        with open(LAST_LINES_FILE_PATH, "x", encoding="utf-8") as file:
            file.write("{}")
    except:
        a = "File already exists so do nothing"

    logMonitor = cLogMonitor(CONFIG_FILE_PATH)
    logMonitor.processDatasets()
    if len(logMonitor.notification.nbody) > 0:
        res = send_pushnotification(logMonitor.notification.nbody, logMonitor.notification.host, logMonitor.notification.path,
                              logMonitor.notification.appToken, logMonitor.notification.userKey,
                              logMonitor.notification.priority, logMonitor.notification.title)
        if res.status != 200:
            my_logger.error("push notification error: " + res.reason)
        else:
            my_logger.info("push notification sent")

    if len(logMonitor.mail.mbody) > 0:
        email = EmailClient(logMonitor.mail.host, logMonitor.mail.port, logMonitor.mail.user, logMonitor.mail.password, logMonitor.mail.useTls, logMonitor.mail.sender, logMonitor.mail.recipient)
        if email.send_email(logMonitor.mail.subject, logMonitor.mail.mbody):
            logMonitor.offsets.remove_old_and_save(logMonitor.processed_files)
    else:
        logMonitor.offsets.remove_old_and_save(logMonitor.processed_files)

    my_logger.info("Done")

    quit(0)
