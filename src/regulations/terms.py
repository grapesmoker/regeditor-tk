from inflect import engine

inf = engine()

class Term:

    def __init__(self, term, defined_in):
        self.term = term
        self.defined_in = defined_in
        self.plural = inf.plural(term)