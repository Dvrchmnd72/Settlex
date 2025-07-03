class Paragraph:
    def __init__(self, text=''):
        self.text = text

class Document:
    def __init__(self, *args, **kwargs):
        self.paragraphs = []
    def save(self, file_obj):
        if hasattr(file_obj, 'write'):
            file_obj.write(b'')
