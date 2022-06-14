from html.parser import HTMLParser
from post import Post


class ThreadParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.posts = []
        self.deepness = 0
        self.post = None
        self.post_deepness = -1
        self.reading_attr = None
        self.counting_tags = ['div', 'span']

    def handle_starttag(self, tag, attrs):
        if tag in self.counting_tags:
            self.deepness = self.deepness + 1

        attrs = dict(attrs)

        if not self.post:
            if tag == 'div':
                if _contain_values(attrs, 'class', ['post', 'reply']):
                    self.post = Post()
                    self.post_deepness = self.deepness
                    self.posts.append(self.post)
        else:
            # Parsing the current post content...
            if tag == 'a':
                if 'id' in attrs and _contain_values(attrs, 'class', ['post_anchor']):
                    self.post.id = int(attrs['id'])
            if tag == 'span':
                if _contain_values(attrs, 'class', ['name']):
                    self.reading_attr = 'name'
                if _contain_values(attrs, 'class', ['trip']):
                    self.reading_attr = 'trip'

    def handle_endtag(self, tag):
        if tag in self.counting_tags:
            if self.post and self.deepness == self.post_deepness:
                self.post = None
                self.post_deepness = -1

            self.deepness = self.deepness - 1
            self.reading_attr = None

    def handle_data(self, data):
        if self.reading_attr == 'name':
            self.post.name = data
        if self.reading_attr == 'trip':
            self.post.trip = data


def _contain_values(attrs, req_attr_key, req_attr_values):
    if req_attr_key not in attrs:
        return False

    values = attrs[req_attr_key].split(' ')

    for required_value in req_attr_values:
        if required_value not in values:
            return False

    return True
