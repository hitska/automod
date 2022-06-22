from html.parser import HTMLParser

import post
from post import Post


class ThreadParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.posts = []
        self.deepness = 0
        self.post = None
        self.post_deepness = -1
        self.reading_attr = None
        self.reading_attr_deepness = -1
        self.counting_tags = ['div', 'span']

    def handle_starttag(self, tag, attrs):
        if tag in self.counting_tags:
            self.deepness = self.deepness + 1

        attrs = dict(attrs)

        if not self.post:
            if tag == 'div':
                if _contain_values(attrs, 'class', ['post', 'reply']):
                    self.start_reading_post()
            return

        # Парсим пост self.post...
        if self.reading_attr == 'body':
            # Парсим body поста...
            if tag == 'br':
                self.post.text = self.post.text + '\n'
            if tag == 'a' and ('onclick' in attrs):
                func_call = attrs['onclick'].split("'")
                reply_id = int(func_call[1])
                self.post.answers_to_ids.append(reply_id)

        elif tag == 'a':
            if 'id' in attrs and _contain_values(attrs, 'class', ['post_anchor']):
                self.post.id = int(attrs['id'])
            elif ('data-extension' in attrs) and ('data-src' in attrs) \
                    and ('data-width' in attrs) and ('data-height' in attrs):
                img = post.Image()
                img.src = attrs['data-src']
                img.width = attrs['data-width']
                img.height = attrs['data-height']
                self.post.images.append(img)

        elif tag == 'time':
            if 'title' in attrs:
                self.post.time = attrs['title']

        elif tag == 'span':
            if _contain_values(attrs, 'class', ['name']):
                self.start_reading_tag('name')
            if _contain_values(attrs, 'class', ['trip']):
                self.start_reading_tag('trip')

        elif tag == 'div':
            if _contain_values(attrs, 'class', ['body']):
                self.start_reading_tag('body')
            if _contain_values(attrs, 'class', ['file']):
                self.start_reading_tag('file')

    def handle_endtag(self, tag):
        if tag in self.counting_tags:
            if self.is_reading_post_closed():
                self.end_reading_post()
            if self.is_reading_tag_closed():
                self.end_reading_tag()

            self.deepness = self.deepness - 1

    def handle_data(self, data):
        if self.reading_attr == 'name':
            self.post.name = data
        if self.reading_attr == 'trip':
            self.post.trip = data
        if self.reading_attr == 'body':
            # Этот элемент может включать в себя вложенные теги
            self.post.text = self.post.text + data

    def start_reading_tag(self, tag):
        self.reading_attr = tag
        self.reading_attr_deepness = self.deepness

    def end_reading_tag(self):
        self.reading_attr = None
        self.reading_attr_deepness = -1

    def is_reading_tag_closed(self):
        return self.reading_attr and self.deepness == self.reading_attr_deepness

    def start_reading_post(self):
        self.post = Post()
        self.posts.append(self.post)
        self.post_deepness = self.deepness

    def end_reading_post(self):
        self.post = None
        self.post_deepness = -1

    def is_reading_post_closed(self):
        return self.post and self.deepness == self.post_deepness


def _contain_values(attrs, req_attr_key, req_attr_values):
    if req_attr_key not in attrs:
        return False

    values = attrs[req_attr_key].split(' ')

    for required_value in req_attr_values:
        if required_value not in values:
            return False

    return True
