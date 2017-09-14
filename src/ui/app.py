import os

import Tkinter as tk
import tkFileDialog, tkMessageBox, tkSimpleDialog
import ttk
import re

from lxml import etree
from lxml.html.clean import clean
from bidict import bidict
from copy import deepcopy

from regulations.notice import Notice
from regulations.utils import ALLOWED_CHILDREN, \
    content_allowed_tags, content_open, content_close, marker_types
from views import element_to_view_map
from functools import partial
from views import *
from views.generic import GenericView


class EditorApp(tk.Frame):

    def __init__(self, master=None):

        tk.Frame.__init__(self, master)
        self.master = master
        self.grid(sticky='nesw')
        self.defined_terms = []
        self.work_state_filename = None
        self.notice = None
        self.root_id = None
        self.element_view = None
        self.tree_to_element_map = bidict()

        self.initialize_gui()
        self.master.bind('<<ElemUpdate>>', self.update_node)

    def initialize_gui(self):

        menubar = tk.Menu(self.master)
        menu_file = tk.Menu(menubar)
        menu_action = tk.Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')
        menubar.add_cascade(menu=menu_action, label='Action')
        menu_file.add_command(label='New regulation (Ctrl-N)', command=partial(self.new_notice, 'regulation', None))
        menu_file.add_command(label='New notice (Ctrl-Shift-N)', command=partial(self.new_notice, 'notice', None))
        menu_file.add_command(label='Open notice (Ctrl-O)', command=partial(self.open_notice, None))
        menu_file.add_separator()
        menu_file.add_command(label='Save notice (Ctrl-S)', command=self.save_notice)
        menu_file.add_separator()
        menu_file.add_command(label='Quit (Ctrl-Q)', command=self.master.quit)
        self.master.bind_all('<Control-o>', self.open_notice)
        self.master.bind_all('<Control-s>', self.save_notice)
        self.master.bind_all('<Control-n>', partial(self.new_notice, 'regulation'))
        self.master.bind_all('<Control-Shift-Key-N>', partial(self.new_notice, 'notice'))
        self.master.bind_all('<Control-q>', lambda x: self.master.quit())
        self.master.config(menu=menubar)

        self.left_frame = tk.Frame(self, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.right_frame = tk.Frame(self, borderwidth=1)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)

        self.element_tree = ttk.Treeview(self.left_frame, selectmode='browse')
        x_scroll = ttk.Scrollbar(command=self.element_tree.xview)
        y_scroll = ttk.Scrollbar(command=self.element_tree.yview)
        self.element_tree.configure(xscrollcommand=x_scroll.set)
        self.element_tree.configure(yscrollcommand=y_scroll.set)

        #self.element_tree.heading('path', text='Path')
        self.element_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.element_tree.bind('<<TreeviewSelect>>', self.select_tree_element)
        self.element_tree.bind('<Button-2>', self.tree_context_menu)

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=1)

        print element_to_view_map

    def new_notice(self, notice_type='regulation', *args):

        load = False
        if self.notice is not None:
            message = "You already have a root notice loaded. If you load " + \
            "another root notice, your current set of notices will be replaced. " + \
            "Are you sure you want to do this?"
            result = tkMessageBox.askokcancel('Replace root?', message)
            if result:
                load = True
        else:
            load = True

        if load:
            for child in self.element_tree.get_children():
                self.element_tree.delete(child)
            self.notice = Notice(notice_type=notice_type)
            self.root_id = self.element_tree.insert('', 'end', text=str(self.notice), open=True)
            self.add_element_to_tree(self.notice.tree, self.root_id)

    def open_notice(self, event):

        load = False
        if self.notice is not None:
            message = "You already have a notice loaded. If you load " + \
            "another notice, your current work will be replaced. " + \
            "Are you sure you want to do this?"
            result = tkMessageBox.askokcancel('Replace notice?', message)
            if result:
                load = True
        else:
            load = True

        if load:

            for child in self.element_tree.get_children():
                self.element_tree.delete(child)

            notice_file = tkFileDialog.askopenfilename()
            if notice_file:
                notice = Notice(notice_file)
                self.notice = notice
                self.tree_to_element_map.clear()
                self.root_id = self.element_tree.insert('', 'end', text='{} effective on {}'.format(
                    self.notice.document_number, self.notice.effective_date.strftime('%Y-%m-%d')), open=True)
                self.add_element_to_tree(self.notice.tree, self.root_id)
                self.work_state_filename = notice_file

    def save_notice(self, *args):

        # before we write, we have to deserialize all the content text back into XML elements
        # we cheat by replacing the content element with an identical element build from its
        # deserialized text. we don't want to modify the original tree (or we'd have to
        # modify it back, so we make a deep copy and write that to disk)
        def deserialize_content(root):
            # also clean up empty titles hanging around in changes
            contents = root.findall('.//change/content')
            for content in contents:
                if content.text is None or content.text.strip() == '':
                    content.getparent().remove(content)
            titles = root.findall('.//change/titles')
            for title in titles:
                if title.text is None or title.text.strip() == '':
                    title.getparent().remove(title)
            contents = root.findall('.//paragraph/content')
            for content in contents:
                content_text = '<content>' + content.text + '</content>'
                new_content = etree.fromstring(content_text)
                content.getparent().replace(content, new_content)


        if self.work_state_filename is None:
            notice_file = tkFileDialog.asksaveasfilename()
            if notice_file:
                self.work_state_filename = notice_file
                with open(self.work_state_filename, 'w') as f:
                    tree_copy = deepcopy(self.notice.tree)
                    deserialize_content(tree_copy)
                    f.write(etree.tostring(tree_copy, pretty_print=True, encoding='UTF-8'))
                    tkMessageBox.showinfo('Saved!', 'Saved to {}'.format(self.work_state_filename))
        else:
            with open(self.work_state_filename, 'w') as f:
                tree_copy = deepcopy(self.notice.tree)
                deserialize_content(tree_copy)
                f.write(etree.tostring(tree_copy, pretty_print=True, encoding='UTF-8'))
                tkMessageBox.showinfo('Saved!', 'Saved to {}'.format(self.work_state_filename))

    def add_element_to_tree(self, element, parent):

        # titles and contents don't need to be listed in the tree, they can
        # be managed by the paragraph view directly. in addition, the content
        # needs to be serialized to a string since we don't want to manage the
        # content element's children individually.
        if element.tag == 'content' and element.getparent().tag in ['paragraph', 'interpParagraph']:
            content_text = unicode(etree.tostring(element, encoding='UTF-8'))
            content_text = re.sub(content_open, '', content_text)
            content_text = re.sub(content_close, '', content_text)
            element.text = content_text
        elif element.tag == 'title' and element.getparent().tag in ['paragraph', 'interpParagraph']:
            pass
        else:
            label = element.get('label', None)
            if label is not None:
                if element.tag in ['paragraph', 'interpParagraph']:
                    item_id = self.element_tree.insert(parent, 'end', text=label, open=True)
                else:
                    item_id = self.element_tree.insert(parent, 'end', text=element.tag + ' ' + label, open=True)
            else:
                item_id = self.element_tree.insert(parent, 'end', text=element.tag.replace('{eregs}', ''), open=True)
            self.tree_to_element_map[item_id] = element
            for child in element.getchildren():
                self.add_element_to_tree(child, item_id)

    def select_tree_element(self, item):
        focus = self.element_tree.focus()
        selection = self.element_tree.item(focus)

        if selection is not None:
            elem = self.tree_to_element_map.get(focus, None)
            if elem is not None:
                view = element_to_view_map.get(elem.tag, None)
                # you can only edit content and title directly if they live under a change
                # if elem.tag == 'change' and elem.get('subpath', None) is not None:
                #     children = ['title', 'content']
                # else:
                children = False
                if view is not None:
                    if self.element_view is not None:
                        self.element_view.destroy()
                    if str(view) == str(GenericView):
                        self.element_view = view(elem, master=self.right_frame, attributes=True, children=children)
                    elif elem.tag == 'change':
                        self.element_view = view(elem, master=self.right_frame, attributes=True, children=['title', 'content'])
                    else:
                        self.element_view = view(elem, master=self.right_frame)
                    self.element_view.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
                else:
                    print 'No view registered for tag {}'.format(elem.tag)
            else:
                'No element in tree map for index {}'.format(focus)

    def tree_context_menu(self, event):

        menu = tk.Menu(self.element_tree, tearoff=0)
        focus = self.element_tree.focus()
        selection = self.element_tree.item(focus)
        if selection is not None and focus != '':
            elem = self.tree_to_element_map.get(focus, None)
            if elem is not None:
                tag = elem.tag.replace('{eregs}', '')
                if tag == 'content':
                    parent_tag = elem.getparent().tag
                    allowed_tags = content_allowed_tags(parent_tag)
                else:
                    allowed_tags = ALLOWED_CHILDREN.get(elem.tag.replace('{eregs}', ''), [])

                for child_tag in allowed_tags:
                    menu.add_command(label='Insert {}'.format(child_tag),
                                     command=partial(self.insert_child, child_tag, elem, focus))
                    if child_tag in ['paragraph', 'interpParagraph']:
                        menu.add_command(label='Insert titled {}'.format(child_tag),
                                         command=partial(self.insert_child, child_tag, elem, focus, True))

                menu.add_command(label='Append {}'.format(elem.tag),
                                 command=partial(self.insert_child, elem.tag, elem.getparent(),
                                                 self.element_tree.parent(focus)))
                if elem.tag in ['paragraph', 'interpParagraph']:
                    menu.add_command(label='Append titled {}'.format(elem.tag),
                                     command=partial(self.insert_child, elem.tag, elem.getparent(),
                                                     self.element_tree.parent(focus), True))

                menu.add_separator()
                menu.add_command(label='Move up', command=partial(self.move_node, -1, focus))
                menu.add_command(label='Move down', command=partial(self.move_node, 1, focus))
                menu.add_command(label='Delete {}'.format(tag),
                                 command=partial(self.delete_node, focus))
                menu.post(event.x_root, event.y_root)

    def insert_child(self, tag, parent_elem, parent_id, with_title=False, *args):

        #print 'Inserting child {} into tree at id {} and as parent of {}'.format(tag, parent_id, parent_elem)
        new_id = self.element_tree.insert(parent_id, 'end', text=tag)
        new_elem = etree.Element(tag)
        parent_elem.append(new_elem)
        self.tree_to_element_map[new_id] = new_elem

        if tag in ['section', 'interpSection']:
            prev = self.element_tree.prev(new_id)
            prev_elem = self.tree_to_element_map[prev]
            if prev_elem is not None:
                prev_label = prev_elem.get('label', None)
                if prev_label is not None:
                    split_label = prev_label.split('-')
                    section_number = int(split_label[1])
                    new_label = split_label[0] + '-' + str(section_number + 1)
                    self.element_tree.item(new_id, text='{} {}'.format(tag, new_label))
                    new_elem.set('label', new_label)
                    new_elem.set('sectionNum', str(section_number + 1))

        elif tag in ['paragraph', 'interpParagraph']:
            prev = self.element_tree.prev(new_id)
            prev_elem = self.tree_to_element_map.get(prev, None)

            if prev_elem is not None:
                prev_label = prev_elem.get('label', None)
                if prev_label is not None:
                    split_label = prev_label.split('-')
                    depth = len(split_label) - 2
                    current_marker = split_label[-1]
                    if tag == 'paragraph':
                        next_marker_type = marker_types[depth]
                        next_marker = next_marker_type[next_marker_type.index(current_marker) + 1]
                        new_label = '-'.join(split_label[:-1] + [next_marker])
                        self.element_tree.item(new_id, text=new_label)
                        new_elem.set('label', new_label)
                        new_elem.set('marker', '({})'.format(next_marker))
                    elif tag == 'interpParagraph':
                        if current_marker == 'Interp':
                            next_marker = '1'
                        else:
                            depth = len(split_label) - split_label.index('Interp')
                            next_marker_type = marker_types[depth]
                            print '304: ', depth, next_marker_type
                            next_marker = next_marker_type[next_marker_type.index(current_marker) + 1]
                            new_label = '-'.join(split_label[:-1] + [next_marker])
                            self.element_tree.item(new_id, text=new_label)
                            new_elem.set('label', new_label)
                        new_elem.set('marker', '{}.'.format(next_marker))

            elif parent_elem.tag == 'change':
                new_label = parent_elem.get('label')
                new_elem.set('label', new_label)
                if tag == 'paragraph':
                    new_marker = new_label.split('-')[-1]
                    new_elem.set('marker', '({})'.format(new_marker))
                elif tag == 'interpParagraph':
                    new_marker = '1'
                    new_elem.set('marker', '{}.'.format(new_marker))
                self.element_tree.item(new_id, text=new_label)
            elif parent_elem.tag != 'change':
                parent_label = parent_elem.get('label')
                split_label = parent_label.split('-')
                depth = len(split_label) - 1
                current_marker = split_label[-1]
                if tag == 'paragraph':
                    next_marker_type = marker_types[depth]
                    next_marker = next_marker_type[0]
                    new_label = '-'.join(split_label + [next_marker])
                    self.element_tree.item(new_id, text=new_label)
                    new_elem.set('label', new_label)
                    new_elem.set('marker', '({})'.format(next_marker))
                elif tag == 'interpParagraph':
                    depth = len(split_label) - split_label.index('Interp') + 1
                    next_marker_type = marker_types[depth]
                    if current_marker == 'Interp' or prev_elem is None:
                        next_marker = next_marker_type[0]
                    else:
                        current_marker = prev_elem.get('label').split('-')[-1]
                        print '339:', depth, next_marker_type, current_marker
                        next_marker = next_marker_type[next_marker_type.index(current_marker) + 1]
                    new_label = '-'.join(split_label + [next_marker])
                    self.element_tree.item(new_id, text=new_label)
                    new_elem.set('label', new_label)
                    new_elem.set('marker', '{}.'.format(next_marker))

            if with_title:
                new_title = etree.SubElement(new_elem, 'title')

    def move_node(self, direction, item_id):

        elem = self.tree_to_element_map.get(item_id, None)
        if elem is not None:
            if direction == -1:
                sibling = self.element_tree.prev(item_id)
            elif direction == 1:
                sibling = self.element_tree.next(item_id)

            if sibling is not None and sibling != '':
                parent_id = self.element_tree.parent(item_id)
                sibling_index = self.element_tree.index(sibling)
                self.element_tree.move(item_id, parent_id, sibling_index + direction)
                elem_parent = elem.getparent()
                elem_index = elem_parent.index(elem)
                elem_parent[elem_index + direction] = elem_parent[elem_index]

    def delete_node(self, item_id):

        elem = self.tree_to_element_map.get(item_id, None)
        self.element_tree.delete(item_id)
        elem.getparent().remove(elem)
        del self.tree_to_element_map[item_id]

    def update_node(self, event):

        elem = event.widget.model
        item_id = self.tree_to_element_map.inv[elem]
        label = elem.attrib.get('label', None)
        if label is None:
            if elem.tag == 'changeset':
                pass
        else:
            if elem.tag in ['paragraph', 'interpParagraph']:
                self.element_tree.item(item_id, text=label)
            else:
                self.element_tree.item(item_id, text=elem.tag + ' ' + label)