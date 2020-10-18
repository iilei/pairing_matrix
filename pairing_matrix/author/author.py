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
            # ensure name keeps present
            self._attrs = {**self._attrs, **kwargs, 'email': email}

    def as_dict(self):
        return {
            **self._attrs,
            'profile_url': self._attrs.get('html_url', self._attrs.get('url')),
            'avatar_url': self._attrs.get('avatar_url', self._attrs.get('avatar')),
            'alias': self._attrs.get(
                'alias', self._attrs.get('name', self._attrs.get('email'))
            ),
        }
