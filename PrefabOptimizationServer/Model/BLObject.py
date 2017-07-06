
class BLObject(object):
    """base class for all build logic objects"""

    @classmethod
    def __GetDefaultId(klass):
        import uuid
        return str(uuid.uuid4())

    def __init__(self, **kwargs):
        self._id = str(BLObject.__GetDefaultId())
        return super().__init__(**kwargs)

    @property
    def Id(self):
        """BL Object identifier in model"""
        return self._id

    @Id.setter
    def Id(self, value):
        self._id = value

    @Id.deleter
    def Id(self):
        del self._id


