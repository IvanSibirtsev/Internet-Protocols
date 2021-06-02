from encoder import Base64
from config import Config


class Message:
    def __init__(self, config: Config):
        targets_address = ','.join(f'"{x}" <{x}>' for x in config.recipients)
        self._boundary = f'1234567890987654321'
        subject = Base64.from_string(config.subject or "No subject")
        header = [
            f'From: "{config.fake_name}" <{config.mail}>',
            f'To:{targets_address}',
            f'Subject: =?UTF-8?B?{subject}?=',
            f'Content-type: multipart/mixed; boundary={self._boundary}',
            ''
        ]
        self._header = '\n'.join(header)
        self._text = self.get_text(config.message_file)

    def append(self, message):
        self._text += f'--{self._boundary}\n{message}'

    def end(self):
        self._text += f'\n--{self._boundary}--\n.\n'

    @property
    def content(self):
        return f'{self._header}\n{self._text}'

    @property
    def text(self) -> str:
        return self._text

    @staticmethod
    def get_text(filename):
        with open(filename, 'r', encoding='utf8') as f:
            message = "".join(f.readlines())
        return f'Content-Transfer-Encoding: 8bit\n' \
               f'Content-Type: text/plain; charset=utf-8\n\n' \
               f'{message}'
