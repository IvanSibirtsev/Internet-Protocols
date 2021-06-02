import base64


class Base64:

    @staticmethod
    def from_string(message: str) -> str:
        return base64.b64encode(message.encode()).decode()

    @staticmethod
    def from_file(filename: str) -> str:
        with open(filename, 'rb') as file:
            return base64.b64encode(file.read()).decode()
