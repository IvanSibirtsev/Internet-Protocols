import socket
import ssl
import time

from config import Config
from encoder import Base64
from attacment import Attachment
from message import Message


def request(message: str) -> bytes:
    return (message + '\n').encode()


class SMTP:
    def __init__(self, client: socket.socket):
        self._client = client

    def hello(self) -> 'SMTP':
        self.__send('EHLO server')
        return self

    def authorized(self, login: str, password: str) -> 'SMTP':
        self.__send('AUTH LOGIN')
        self.__send(Base64.from_string(login))
        self.__send(Base64.from_string(password))
        return self

    def make_header(self, sender: str, recipients: list) -> 'SMTP':
        self.__send(f'MAIL FROM: {sender}')
        for recipient in recipients:
            time.sleep(0.5)
            self.__send(f'RCPT TO: {recipient}')
        return self

    def send_data(self, data: str) -> 'SMTP':
        self.__send('DATA')
        self.__send(data)
        return self

    def __send(self, message: str):
        self._client.send(request(message))
        self.__receive()

    def __receive(self):
        print('Server:', self._client.recv(65535)
              .decode().removesuffix('\n'))


def create_message(config: Config) -> str:
    subject = config.subject
    message = Message(config)
    if not config.attachments:
        return f'Subject: =?UTF-8?B?{Base64.from_string(subject)}?=\n{message.text}\n.\n'
    message.append(message.text)
    attachments = [
        Attachment(filename).content for filename in config.attachments]
    [message.append(attachment) for attachment in attachments]
    message.end()
    return message.content


def main():
    config = Config('config.json')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((config.mail_server, config.port))
        client = ssl.wrap_socket(client)
    smtp = SMTP(client)
    (smtp.hello()
        .authorized(config.name, config.password)
        .make_header(config.mail, config.recipients)
        .send_data(create_message(config)))


if __name__ == '__main__':
    main()
