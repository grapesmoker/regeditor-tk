import Tkinter as tk
from lxml import etree

element_to_view_map = {}

# this is a mixin class that is used to implement data binding between views
# and models; it shouldn't be instantiated on its own because it has no model
# without deriving a specific type of view from it


class ViewWithUpdate:

    def update_model(self, child_tag, var, *args):

        child = self.model.find(child_tag)
        if child is None:
            # handle updates to arbitrary subelements
            if '/' in child_tag:
                #import ipdb; ipdb.set_trace()
                path = child_tag.split('/')
                current_elem = self.model
                for path_child in path:
                    parent = current_elem.find(path_child)
                    if parent is None:
                        current_elem = etree.SubElement(current_elem, path_child)
                    else:
                        current_elem = parent
                current_elem.text = str(var.get())
            else:
                child = etree.SubElement(self.model, child_tag)
                child.text = str(var.get())
        else:
            child.text = str(var.get())

    def update_view(self, child_tag, var, value_type):

        #print 'updating {} from element {}'.format(str(var), child_tag)
        child = self.model.find(child_tag)
        if child is not None:
            var.set(value_type(child.text))

    def update_view_attribute(self, attribute, var, value_type):

        value = self.model.attrib.get(attribute, None)
        if value is not None:
            var.set(value_type(value))

    def update_model_attribute(self, attribute, var, *args):

        value = str(var.get()).strip()
        if value == '':
            del self.model.attrib[attribute]
        else:
            self.model.attrib[attribute] = value
        self.event_generate('<<ElemUpdate>>')


class ViewBase(tk.Frame):

    _passthrough_args = ['attributes', 'children']

    def __init__(self, model, *args, **kwargs):
        self.view_args = {arg: kwargs.pop(arg, None) for arg in self._passthrough_args}
        tk.Frame.__init__(self, *args, **kwargs)
        self.model = model

__all__ = ['decorators', 'generic', 'notice', 'paragraphs', 'element_to_view_map']