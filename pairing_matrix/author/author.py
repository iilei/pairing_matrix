class Author:
    def __init__(self, email, **kwargs):
        self._attrs = {'email': email, **kwargs}

    @property
    def email(self):
        return self._attrs.get('email')

    @property
    def name(self):
        return self._attrs.get('name')

    @property
    def url(self):
        return self._attrs.get('url')

    @property
    def avatar(self):
        return self._attrs.get('avatar')

    def update(self, email, **kwargs):
        if email == self._attrs.get('email'):
            _name = self._attrs.get('name')
            # ensure name keeps present even if not provided
            self._attrs = {'name': _name, 'email': email, **kwargs}

    def as_dict(self):
        return {
            'email': self._attrs.get('email'),
            'name': self._attrs.get('name'),
            'url': self._attrs.get('url'),
            'avatar': self._attrs.get('avatar'),
        }
