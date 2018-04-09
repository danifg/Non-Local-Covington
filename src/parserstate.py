"""
Parser state of transition-based parsers.
"""

from copy import copy

class ParserState:
    def __init__(self, sentence, transsys=None, goldrels=None):
        self.list1 = [0]
        self.list2 = []
        # sentences should already have a <ROOT> symbol as the first token
        self.buf = [i+1 for i in xrange(len(sentence)-1)]
        # head and relation labels
        self.head = [[-1, -1] for _ in xrange(len(sentence))]

        self.pos = [-1 for _ in xrange(len(sentence))]

        self.goldrels = goldrels

        self.transsys = transsys
        if self.transsys is not None:
            self.transsys._preparetransitionset(self)

    def show_head(self):
        a=self.head[1:len(self.head)]
        print a
        for x,y in a:
            if x == -1:
               print a 
        
        
    
    def transitionset(self):
        return self._transitionset

    def clone(self):
        res = ParserState([])
        res.list1 = copy(self.list1)
        res.list2 = copy(self.list2)
        res.buf = copy(self.buf)
        res.head = copy(self.head)
        res.pos = copy(self.pos)
        res.goldrels = copy(self.goldrels)
        res.transsys = self.transsys
        if hasattr(self, '_transitionset'):
            res._transitionset = copy(self._transitionset)
        return res
