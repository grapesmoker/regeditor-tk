from . import element_to_view_map


def register_view(*args):

    def wrapper(cls):

        for tag_name in args:
            element_to_view_map[tag_name] = cls

        return cls

    return wrapper