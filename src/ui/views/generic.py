import Tkinter as tk
from . import ViewWithUpdate, ViewBase
from decorators import register_view
from regulations.utils import ALLOWED_CHILDREN, ALLOWED_ATTRIBUTES
from functools import partial


@register_view('tocSecEntry', 'part', 'subpart', 'section', 'changeset', 'change')
class GenericView(ViewBase, ViewWithUpdate):

    def __init__(self, *args, **kwargs):

        ViewBase.__init__(self, *args, **kwargs)
        attributes = self.view_args.get('attributes', None)
        children = self.view_args.get('children', None)

        row = 0
        if attributes:
            if type(attributes) is bool:
                attributes = ALLOWED_ATTRIBUTES.get(self.model.tag, [])
            elif type(attributes) is list:
                pass
            else:
                raise TypeError('Invalid type of attributes!')
            for attr in attributes:
                attr_var_name = str(attr) + '_var'
                label = tk.Label(self, text=attr)
                self.__dict__[attr_var_name] = tk.StringVar(self)
                self.__dict__[attr] = tk.Entry(self, textvariable=self.__dict__[attr_var_name])
                widget = self.__dict__[attr]
                label.grid(row=row, column=0)
                widget.grid(row=row, column=1)
                row += 1

                self.update_view_attribute(attr, self.__dict__[attr_var_name], str)
                self.__dict__[attr_var_name].trace('w', partial(self.update_model_attribute,
                                                                attr,
                                                                self.__dict__[attr_var_name]))

        if children:
            if type(children) is bool:
                children = ALLOWED_CHILDREN.get(self.model.tag, [])
            elif type(children) is list:
                pass
            else:
                raise TypeError('Invalid type of children!')
            for child in children:

                child_var_name = child + '_var'
                label = tk.Label(self, text=child)
                self.__dict__[child_var_name] = tk.StringVar(self)
                self.__dict__[child] = tk.Entry(self, textvariable=self.__dict__[child_var_name])
                widget = self.__dict__[child]
                label.grid(row=row, column=0)
                widget.grid(row=row, column=1)
                row += 1

                self.update_view(child, self.__dict__[child_var_name], str)
                self.__dict__[child_var_name].trace('w', partial(self.update_model,
                                                                 child,
                                                                 self.__dict__[child_var_name]))
