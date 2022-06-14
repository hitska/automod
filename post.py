
class Post:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.trip = ''
        self.text = ''

    def __str__(self):
        return f'id {self.id}, name {self.name}, trip {self.trip}: {self.text}'
