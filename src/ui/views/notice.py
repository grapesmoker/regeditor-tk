import Tkinter as tk
import re

from lxml import etree
from functools import partial

from . import ViewWithUpdate, ViewBase
from decorators import register_view
from generic import GenericView


@register_view('fdsys')
class FdsysView(ViewBase, ViewWithUpdate):

    def __init__(self, *args, **kwargs):
        ViewBase.__init__(self, *args, **kwargs)

        label = tk.Label(self, text='CFR title number')
        self.cfr_title_var = tk.IntVar(self)
        self.cfr_title = tk.Entry(self, textvariable=self.cfr_title_var)
        label.grid(row=0, column=0)
        self.cfr_title.grid(row=0, column=1)

        label = tk.Label(self, text='CFR title text')
        self.cfr_title_text_var = tk.StringVar(self)
        self.cfr_title_text = tk.Entry(self, textvariable=self.cfr_title_text_var)
        label.grid(row=1, column=0)
        self.cfr_title_text.grid(row=1, column=1)

        label = tk.Label(self, text='Volume')
        self.volume_var = tk.IntVar(self)
        self.volume = tk.Entry(self, textvariable=self.volume_var)
        label.grid(row=2, column=0)
        self.volume.grid(row=2, column=1)

        label = tk.Label(self, text='Date')
        self.date_var = tk.StringVar(self)
        self.date = tk.Entry(self, textvariable=self.date_var)
        label.grid(row=3, column=0)
        self.date.grid(row=3, column=1)

        label = tk.Label(self, text='Original date')
        self.orig_date_var = tk.StringVar(self)
        self.orig_date = tk.Entry(self, textvariable=self.orig_date_var)
        label.grid(row=4, column=0)
        self.orig_date.grid(row=4, column=1)

        label = tk.Label(self, text='Title')
        self.title_var = tk.StringVar(self)
        self.title = tk.Entry(self, textvariable=self.title_var)
        label.grid(row=5, column=0)
        self.title.grid(row=5, column=1)

        self.update_view('cfrTitleNum', self.cfr_title_var, int)
        self.update_view('cfrTitleText', self.cfr_title_text_var, str)
        self.update_view('volume', self.volume_var, int)
        self.update_view('date', self.date_var, str)
        self.update_view('originalDate', self.orig_date_var, str)
        self.update_view('title', self.title_var, str)

        self.cfr_title_var.trace('w', partial(self.update_model, 'cfrTitleNum', self.cfr_title_var))
        self.cfr_title_text_var.trace('w', partial(self.update_model, 'cfrTitleText', self.cfr_title_text_var))
        self.volume_var.trace('w', partial(self.update_model, 'volume', self.volume_var))
        self.date_var.trace('w', partial(self.update_model, 'date', self.date_var))
        self.orig_date_var.trace('w', partial(self.update_model, 'originalDate', self.orig_date_var))
        self.title_var.trace('w', partial(self.update_model, 'title', self.title_var))


@register_view('preamble')
class PreambleView(tk.Frame, ViewWithUpdate):

    def __init__(self, preamble, master=None):
        tk.Frame.__init__(self, master)
        self.model = preamble

        label = tk.Label(self, text='Agency')
        self.agency_var = tk.StringVar(self)
        self.agency = tk.Entry(self, textvariable=self.agency_var)
        label.grid(row=0, column=0)
        self.agency.grid(row=0, column=1)

        label = tk.Label(self, text='Regulation letter')
        self.reg_letter_var = tk.StringVar(self)
        self.reg_letter = tk.Entry(self, textvariable=self.reg_letter_var)
        label.grid(row=1, column=0)
        self.reg_letter.grid(row=1, column=1)

        label = tk.Label(self, text='CFR title')
        self.cfr_title_var = tk.IntVar(self)
        self.cfr_title = tk.Entry(self, textvariable=self.cfr_title_var)
        label.grid(row=2, column=0)
        self.cfr_title.grid(row=2, column=1)

        label = tk.Label(self, text='CFR section')
        self.cfr_section_var = tk.IntVar(self)
        self.cfr_section = tk.Entry(self, textvariable=self.cfr_section_var)
        label.grid(row=3, column=0)
        self.cfr_section.grid(row=3, column=1)

        label = tk.Label(self, text='Document number')
        self.doc_number_var = tk.StringVar(self)
        self.doc_number = tk.Entry(self, textvariable=self.doc_number_var)
        label.grid(row=4, column=0)
        self.doc_number.grid(row=4, column=1)

        label = tk.Label(self, text='Effective date')
        self.effective_date_var = tk.StringVar(self)
        self.effective_date = tk.Entry(self, textvariable=self.effective_date_var)
        label.grid(row=5, column=0)
        self.effective_date.grid(row=5, column=1)

        label = tk.Label(self, text='Federal register URL')
        self.url_var = tk.StringVar(self)
        self.url = tk.Entry(self, textvariable=self.url_var)
        label.grid(row=6, column=0)
        self.url.grid(row=6, column=1)

        self.update_view('agency', self.agency_var, str)
        self.update_view('regLetter', self.reg_letter_var, str)
        self.update_view('cfr/title', self.cfr_title_var, int)
        self.update_view('cfr/section', self.cfr_section_var, int)
        self.update_view('documentNumber', self.doc_number_var, str)
        self.update_view('effectiveDate', self.effective_date_var, str)
        self.update_view('federalRegisterURL', self.url_var, str)

        self.agency_var.trace('w', partial(self.update_model, 'agency', self.agency_var))
        self.reg_letter_var.trace('w', partial(self.update_model, 'regLetter', self.reg_letter_var))
        self.cfr_title_var.trace('w', partial(self.update_model, 'cfr/title', self.cfr_title_var))
        self.cfr_section_var.trace('w', partial(self.update_model, 'cfr/section', self.cfr_section_var))
        self.doc_number_var.trace('w', partial(self.update_model, 'documentNumber', self.doc_number_var))
        self.effective_date_var.trace('w', partial(self.update_model, 'effectiveDate', self.effective_date_var))
        self.url_var.trace('w', partial(self.update_model, 'federalRegisterURL', self.url_var))


@register_view('change')
class ChangeView(GenericView):

    def __init__(self, *args, **kwargs):
        GenericView.__init__(self, *args, **kwargs)

        if 'content_var' in self.__dict__:
            del self.__dict__['content_var']
        if 'content' in self.__dict__:
            self.content.destroy()
            del self.__dict__['content']

        #import ipdb; ipdb.set_trace()
        label = tk.Label(self, text='Content', borderwidth=1)
        self.content = tk.Text(self, wrap=tk.WORD, height=35)
        label.grid(row=self.size, column=0)
        self.content.grid(row=self.size, column=1, sticky='e')
        self.content.bind('<KeyRelease>', self.update_content)

        if self.model.find('content') is None:
            content = etree.SubElement(self.model, 'content')
            content.text = ''
        self.content.insert(1.0, self.model.find('content').text.strip())

    def update_content(self, *args):

        content_text = self.content.get(1.0, tk.END).strip()
        self.model.find('content').text = content_text