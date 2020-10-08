class Author:
    def __init__(self, email, **kwargs):
        self._attrs = {'email': email, **kwargs}

    @property
    def email(self):
        return self._attrs.get('email')
