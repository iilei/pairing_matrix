class Author:
    def __init__(self, email, **kwargs):
        self._attrs = {'email': email, **kwargs}

    @property
    def email(self):
        return self._attrs.get('email')

    @property
    def name(self):
        return self._attrs.get('name')

    def update(self, email, **kwargs):
        if email == self._attrs.get('email'):
            _name = self._attrs.get('name')
            # ensure name keeps present even if not provided
            self._attrs = {'name': _name, 'email': email, **kwargs}
