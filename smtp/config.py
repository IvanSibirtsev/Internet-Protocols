import json


class Config:
    def __init__(self, filename: str):
        with open(filename, encoding='utf8') as config:
            conf = json.load(config)
            self.mail_server = conf['mail_server']
            self.port = conf['port']
            self.mail = conf['mail']
            self.fake_name = conf['name']
            self.name = conf['name']
            self.password = conf['password']
            self.recipients = conf['recipients']
            self.message_file = conf['message_file']
            self.subject = conf['subject']
            self.attachments = conf['attachments']
