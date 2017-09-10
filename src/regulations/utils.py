import re
import itertools
import string

ALLOWED_CHILDREN = {
    'regulation': ['fdsys', 'preamble', 'part'],
    'fdsys': ['cfrTitleNum', 'cfrTitleText', 'volume', 'date', 'originalDate', 'title'],
    'preamble': ['agency', 'regLetter', 'cfr', 'documentNumber', 'effectiveDate', 'federalRegisterURL'],
    'cfr': ['title', 'section'],
    'part': ['tableOfContents', 'content'],
    'tableOfContents': ['tocSecEntry', 'tocAppEntry', 'tocInterpEntry'],
    'tocSecEntry': ['sectionNum', 'sectionSubject'],
    'tocAppEntry': ['appendixLetter', 'appendixSubject'],
    'tocInterpEntry': ['interpTitle'],
    'content': ['subpart', 'section'],
    'subpart': ['content', 'interpretations'],
    'section': ['subject', 'paragraph'],
    'paragraph': ['title', 'content', 'paragraph'],
    'interpretations': ['title', 'interpSection'],
    'interpSection': ['title', 'interpParagraph'],
    'interpParagraph': ['title', 'interpParagraph'],
    'notice': ['fdsys', 'preamble', 'changeset'],
    'changeset': ['change'],
    'change': ['section', 'interpSection', 'paragraph', 'interpParagraph']
}

ALLOWED_ATTRIBUTES = {
    'part': ['label'],
    'tocSecEntry': ['target'],
    'tocAppEntry': ['target'],
    'tocInterpEntry': ['target'],
    'subpart': ['label'],
    'section': ['label', 'sectionNum'],
    'paragraph': ['label', 'marker'],
    'interpretations': ['label'],
    'interpSection': ['label'],
    'interpParagraph': ['label', 'target', 'marker'],
    'changeset': ['leftDocumentNumber', 'leftEffectiveDate', 'rightDocumentNumber'],
    'change': ['operation', 'label', 'parent', 'before', 'after', 'subpath'],
}


def content_allowed_tags(parent_tag):

    if parent_tag in ['paragraph', 'interpParagraph']:
        return []
    elif parent_tag == 'part':
        return ['subpart']
    elif parent_tag == 'subpart':
        return ['section']
    else:
        return []


def roman_nums():
    """Generator for roman numerals."""
    mapping = [
        (1, 'i'), (4, 'iv'), (5, 'v'), (9, 'ix'),
        (10, 'x'), (40, 'xl'), (50, 'l'), (90, 'xc'),
        (100, 'c'), (400, 'cd'), (500, 'd'), (900, 'cm'),
        (1000, 'm')
        ]
    i = 1
    while True:
        next_str = ''
        remaining_int = i
        remaining_mapping = list(mapping)
        while remaining_mapping:
            (amount, chars) = remaining_mapping.pop()
            while remaining_int >= amount:
                next_str += chars
                remaining_int -= amount
        yield next_str
        i += 1

content_open = re.compile('<content (.*?)>')
content_close = re.compile('</content>')

lower = (tuple(string.ascii_lowercase) +
         tuple(a+a for a in string.ascii_lowercase))
upper = (tuple(string.ascii_uppercase) +
         tuple(a+a for a in string.ascii_uppercase))

ints = tuple(str(i) for i in range(1, 51))
roman = tuple(itertools.islice(roman_nums(), 0, 50))

marker_types = {
    1: lower,
    2: ints,
    3: roman,
    4: upper,
    5: ints
}
