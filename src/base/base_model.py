from bson import ObjectId


class Serializable(dict):
    def __init__(self):
        super().__init__()

        __getattr__ = dict.get
        __delattr__ = dict.__delitem__
        __setattr__ = dict.__setitem__
