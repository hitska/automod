class Post:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.trip = ''
        self.time = ''
        self.text = ''
        self.images = []
        self.answers_to_ids = []

    def __str__(self):
        image_count = len(self.images)
        return f'id({self.id}), name({self.name}), trip({self.trip}), time({self.time}), images({image_count}),'\
               f' text({self.text})'

class Image:
    def __init__(self):
        self.src = ''
        self.height = 0
        self.width = 0
