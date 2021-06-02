import mimetypes
import os

from encoder import Base64


class Attachment:
    def __init__(self, filename: str):
        file_extension = os.path.splitext(filename)[1]
        content_type = mimetypes.types_map[file_extension]
        name = filename.split('/')[-1]
        base64_filename = f'"=?UTF-8?B?{Base64.from_string(name)}?="'
        base64_attachment = Base64.from_file(filename)
        content = [
            f'Content-Type: {content_type}; name={base64_filename}',
            f'Content-Disposition: attachment; filename={base64_filename}',
            f'Content-Transfer-Encoding: base64',
            '',
            f'{base64_attachment}'
        ]
        self.content = '\n'.join(content)
