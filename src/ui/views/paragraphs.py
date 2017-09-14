import Tkinter as tk
from . import ViewBase, ViewWithUpdate
from decorators import register_view
from functools import partial
from lxml import etree


@register_view('paragraph', 'interpParagraph')
class ParagraphView(ViewBase, ViewWithUpdate):

    def __init__(self, *args, **kwargs):
        ViewBase.__init__(self, *args, **kwargs)

        row = 0

        label = tk.Label(self, text='Label')
        self.label_var = tk.StringVar(self)
        self.label = tk.Entry(self, textvariable=self.label_var, width=40)
        label.grid(row=row, column=0)
        self.label.grid(row=row, column=1, sticky='e')
        self.update_view_attribute('label', self.label_var, str)
        self.label_var.trace('w', partial(self.update_model_attribute, 'label', self.label_var))
        row += 1

        if self.model.tag == 'interpParagraph':
            label = tk.Label(self, text='Target')
            self.target_var = tk.StringVar(self)
            self.target = tk.Entry(self, textvariable=self.target_var, width=40)
            label.grid(row=row, column=0)
            self.target.grid(row=row, column=1, sticky='e')
            self.update_view_attribute('target', self.target_var, str)
            self.target_var.trace('w', partial(self.update_model_attribute, 'target', self.target_var))
            row += 1

        label = tk.Label(self, text='Marker')
        self.marker_var = tk.StringVar(self)
        self.marker = tk.Entry(self, textvariable=self.marker_var, width=10)
        label.grid(row=row, column=0)
        self.marker.grid(row=row, column=1, sticky='e')
        self.update_view_attribute('marker', self.marker_var, str)
        self.marker_var.trace('w', partial(self.update_model_attribute, 'marker', self.marker_var))
        row += 1

        if self.model.find('title') is not None:
            label = tk.Label(self, text='Title')
            self.title_var = tk.StringVar(self)
            self.title = tk.Entry(self, textvariable=self.title_var, width=80)
            label.grid(row=row, column=0)
            self.title.grid(row=row, column=1, sticky='e')
            self.update_view('title', self.title_var, str)
            self.title_var.trace('w', partial(self.update_model, 'title', self.title_var))
            row += 1

        label = tk.Label(self, text='Content', borderwidth=1)
        self.content = tk.Text(self, wrap=tk.WORD, height=35)
        label.grid(row=row, column=0)
        self.content.grid(row=row, column=1, sticky='e')
        self.content.bind('<KeyRelease>', self.update_content)

        if self.model.find('content') is None:
            content = etree.SubElement(self.model, 'content')
            content.text = ''
        self.content.insert(1.0, self.model.find('content').text.strip())

        row += 1

    def update_content(self, *args):

        content_text = self.content.get(1.0, tk.END).strip()
        #print 'setting text to:', content_text
        self.model.find('content').text = content_text
