import random
from tarjan import tarjan
import sys


"""
Implementation of transition systems.

The TransitionSystem class is an "interface" for all of the
subclasses that are being used, but isn't really used anywhere
explicitly itself.
"""

class TransitionSystem(object):
    def __init__(self, mappings, invmappings,epoch=1):
        self.mappings, self.invmappings = mappings, invmappings
        self.epoch=epoch
        random.seed(epoch)

    def _preparetransitionset(self, parserstate):
        """ Prepares the set of gold transitions given a parser state """
        raise NotImplementedError()

    def advance(self, parserstate, action):
        """ Advances a parser state given an action """
        raise NotImplementedError()

    def goldtransition(self, parserstate, goldrels):
        """ Returns the next gold transition given the set of gold arcs """
        raise NotImplementedError()

    def trans_to_str(self, transition, state, pos, fpos=None):
        raise NotImplementedError()

    @classmethod
    def trans_from_line(self, line):
        raise NotImplementedError()

    @classmethod
    def actions_list(self):
        raise NotImplementedError()



class Covington(TransitionSystem):
    @classmethod
    def actions_list(self):
        return [ 'NoArc', 'Shift', 'Left-Arc', 'Right-Arc']

    def create_cycles(self, parserstate, h, d):
        head = parserstate.head
        n = h
        
        if n == d:
            return True 
        
        while n > 0:
            n = head[n][0]
            if n == d:
                return True 
        return False

    def _preparetransitionset(self, parserstate):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        
        list1, list2, buf, head = parserstate.list1, parserstate.list2, parserstate.buf, parserstate.head

        t = []
        
        if len(buf) != 0:
            
            if len(list1) == 0:
                t += [(SHIFT, -1)]
            else:  
                t += [(NOARC, -1)]
                t += [(SHIFT, -1)]
                if list1[len(list1)-1] != 0 and head[list1[len(list1)-1]][0] < 0 and not self.create_cycles(parserstate, head[buf[0]][0], list1[len(list1)-1]):
                    t += [(LEFTARC,)]
            
                if head[buf[0]][0] < 0 and not self.create_cycles(parserstate, head[list1[len(list1)-1]][0], buf[0]):
                    t += [(RIGHTARC,)]
                
        parserstate._transitionset = t
    
    
        
    def advance(self, parserstate, action):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])
        cand = parserstate.transitionset()

       
        
        if isinstance(action, int):
           a, rel = self.tuple_trans_from_int(cand, action)
        else:
           rel = action[-1]
           a = action[:-1]

        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        
        if a[0] == LEFTARC:
            n = len(list1)-1 
            parserstate.head[list1[n]] = [buf[0], rel]
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
        elif a[0] == RIGHTARC:
            n = len(list1)-1 
            parserstate.head[buf[0]] = [list1[n], rel]
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
        
        elif a[0] == SHIFT:
            parserstate.list1 = list1+list2+[buf[0]]
            parserstate.list2 = [];
            parserstate.buf = buf[1:]
        else:
            n = len(list1)-1
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
            
        self._preparetransitionset(parserstate)

    def goldtransition(self, parserstate, goldrels=None):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        goldrels = goldrels or parserstate.goldrels
        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        head = parserstate.head

        r = buf[0]
        addedArc = False
        noleftchildren = True
        for x in list1:
            if x in goldrels[r]:
                noleftchildren = False
                break    
        
        
        norighthead = True
        for x in list1:
            if r in goldrels[x]:
                norighthead = False
                break
        
        
        
        if len(list1) == 0:
            a = (SHIFT, -1)
            return a
            
        
        l = list1[len(list1)-1]     
        if l in goldrels[r]:
            rel = goldrels[r][l]
            a = (LEFTARC, rel)
        elif r in goldrels[l]:
            rel = goldrels[l][r]
            a = (RIGHTARC, rel)
        elif norighthead and noleftchildren:
            a = (SHIFT, -1)
        else:
            a = (NOARC, -1)
        
        return a

    def trans_to_str(self, t, state, pos, fpos=None):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        if t[0] == SHIFT:
            if fpos is None:
                return "Shift\t%s" % (pos[state.buf[0]])
            else:
                return "Shift\t%s\t%s" % (pos[state.buf[0]], fpos[state.buf[0]])
        elif t[0] == LEFTARC:
            return "Left-Arc\t%s" % (self.invmappings['rel'][t[1]])
        elif t[0] == RIGHTARC:
            return "Right-Arc\t%s" % (self.invmappings['rel'][t[1]])
        elif t[0] == NOARC:
            return "NoArc"

    @classmethod
    def trans_from_line(self, line):
        if line[0] == 'Left-Arc':
            fields = { 'action':line[0], 'rel':line[1] }
        elif line[0] == 'Right-Arc':
            fields = { 'action':line[0], 'rel':line[1] }
        elif line[0] == 'Shift':
            fields = { 'action':line[0], 'pos':line[1] }
            if len(line) > 2:
                fields['fpos'] = line[2]
        elif line[0] == 'NoArc':
            fields = { 'action':line[0] }        
        else:
            raise ValueError(line[0])
        return fields
    

    def tuple_trans_to_int(self, cand, t):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])

        base = 0
        
        if t[0] == NOARC:
            return base

        base += 1


        
        if t[0] == SHIFT:
            return base

        base += 1

        if t[0] == LEFTARC:
            return base + t[1]

        base += RELS

        if t[0] == RIGHTARC:
            return base + t[1]

    def tuple_trans_from_int(self, cand, action):
        NOARC = self.mappings['action']['NoArc']
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        RELS = len(self.mappings['rel'])
        rel = -1
        
        base = 0
        if action == base:
            a = (NOARC, -1)
        base += 1

        if action == base:
            a = (SHIFT, -1)
        base += 1

        if base <= action < base + RELS:
            a = (LEFTARC,)
            rel = action - base
        base += RELS

        if base <= action < base + RELS:
            a = (RIGHTARC,)
            rel = action - base

        return a, rel








class NewCovington(TransitionSystem):
    @classmethod
    def actions_list(self):
        return [ 'Shift', 'Left-Arc', 'Right-Arc']

    def create_cycles(self, parserstate, h, d):
        head = parserstate.head
        n = h
        
        if n == d:
            return True 
        
        while n > 0:
            n = head[n][0]
            if n == d:
                return True 
        return False

    def _preparetransitionset(self, parserstate):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        
        list1, list2, buf, head = parserstate.list1, parserstate.list2, parserstate.buf, parserstate.head

        t = []
        if len(buf) != 0:
            
        
            if len(list1) == 0:
                t += [(SHIFT, -1)]
            else:  
                t += [(SHIFT, -1)]
                
                
                for si in xrange(len(list1)):
                    n = len(list1)-1
                    li = n - si
                    if list1[li] != 0 and head[list1[li]][0] < 0 and not self.create_cycles(parserstate, head[buf[0]][0], list1[li]):
                        t += [(LEFTARC, si)]
                    
                for si in xrange(len(list1)):
                    n = len(list1)-1
                    li = n - si
                    
                    if head[buf[0]][0] < 0 and not self.create_cycles(parserstate, head[list1[li]][0], buf[0]):
                        t += [(RIGHTARC, si)]
                
           
        
        parserstate._transitionset = t
    
    
        
    def advance(self, parserstate, action):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])
        cand = parserstate.transitionset()

       
        
        if isinstance(action, int):
           a, rel = self.tuple_trans_from_int(cand, action)
           
        else:
           rel = action[-1]
           a = action[:-1]

        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        
        
        if a[0] == LEFTARC:
            n = len(list1)-1
            si = a[1] 
            parserstate.head[list1[n-si]] = [buf[0], rel]
            parserstate.list2 = list1[(n-si):]+list2
            parserstate.list1 = list1[:(n-si)]
        elif a[0] == RIGHTARC:
            n = len(list1)-1
            si = a[1] 
            parserstate.head[buf[0]] = [list1[n-si], rel]
            parserstate.list2 = list1[(n-si):]+list2
            parserstate.list1 = list1[:(n-si)]
        
        elif a[0] == SHIFT:
            parserstate.list1 = list1+list2+[buf[0]]
            parserstate.list2 = [];
            parserstate.buf = buf[1:]
            
       
        self._preparetransitionset(parserstate)

    def goldtransition(self, parserstate, goldrels=None):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        goldrels = goldrels or parserstate.goldrels
        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        head = parserstate.head

        r = buf[0]
        addedArc = False
        
        if len(list1) == 0:
            a = (SHIFT, -1, -1)
            return a
            
        for si in xrange(len(list1)):
            n =len(list1)-1
            li = n-si
            l = list1[li]     
            if l in goldrels[r]:
                rel = goldrels[r][l]
                a = (LEFTARC, si, rel)
                addedArc = True
                break
            elif r in goldrels[l]:
                rel = goldrels[l][r]
                a = (RIGHTARC, si, rel)
                addedArc = True
                break
       
        if not addedArc:
            a = (SHIFT, -1, -1)
        
	return a

    def trans_to_str(self, t, state, pos, fpos=None):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        if t[0] == SHIFT:
            if fpos is None:
                return "Shift\t%s" % (pos[state.buf[0]])
            else:
                return "Shift\t%s\t%s" % (pos[state.buf[0]], fpos[state.buf[0]])
        elif t[0] == LEFTARC:
            return "Left-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        elif t[0] == RIGHTARC:
            return "Right-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        
    @classmethod
    def trans_from_line(self, line):
        if line[0] == 'Left-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Right-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Shift':
            fields = { 'action':line[0], 'pos':line[1] }
            if len(line) > 2:
                fields['fpos'] = line[2]
        else:
            raise ValueError(line[0])
        return fields
    

    def tuple_trans_to_int(self, cand, t, num_la=0, num_ra=0,num_la_total=0):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])


        base = 0
        if t[0] == SHIFT:
            return 0

        if cand[0][0] == SHIFT:
            base = 1

        if t[0] == LEFTARC:
            return base + num_la*RELS + t[2]
        
        if t[0] == RIGHTARC:
            return base + num_la_total*RELS + num_ra*RELS + t[2]

    def tuple_trans_from_int(self, cand, action):
        
        
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        RELS = len(self.mappings['rel'])
        rel = -1
        
        if cand[0][0] == SHIFT:
            if action == 0:
                a = cand[0]
            else:
                a = cand[(action - 1) / RELS + 1]
                rel = (action - 1) % RELS
        else:
            a = cand[action / RELS]
            rel = action % RELS

        return a, rel
    
    
class Covington2(TransitionSystem):
    @classmethod
    def actions_list(self):
        return [ 'Shift', 'NoArc', 'Left-Arc', 'Right-Arc']

    def create_cycles(self, parserstate, h, d):
        head = parserstate.head
        n = h
        
        if n == d:
            return True 
        
        while n > 0:
            n = head[n][0]
            if n == d:
                return True 
        return False

    def _preparetransitionset(self, parserstate):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        
        list1, list2, buf, head = parserstate.list1, parserstate.list2, parserstate.buf, parserstate.head

        t = []
        
        if len(buf) != 0:
            
            if len(list1) == 0:
                t += [(SHIFT, -1)]
            else:  
                t += [(SHIFT, -1)]
                t += [(NOARC, 0)]
                if list1[len(list1)-1] != 0 and head[list1[len(list1)-1]][0] < 0 and not self.create_cycles(parserstate, head[buf[0]][0], list1[len(list1)-1]):
                    t += [(LEFTARC, 0)]
            
                if head[buf[0]][0] < 0 and not self.create_cycles(parserstate, head[list1[len(list1)-1]][0], buf[0]):
                    t += [(RIGHTARC, 0)]
        
        parserstate._transitionset = t
    
    
        
    def advance(self, parserstate, action):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])
        cand = parserstate.transitionset()

       
         
        if isinstance(action, int):
           a, rel = self.tuple_trans_from_int(cand, action)
        else:
           rel = action[-1]
           a = action[:-1]

        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
  
        
        
        if a[0] == LEFTARC:
            n = len(list1)-1 
            parserstate.head[list1[n]] = [buf[0], rel]
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
        elif a[0] == RIGHTARC:
            n = len(list1)-1 
            parserstate.head[buf[0]] = [list1[n], rel]
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
        
        elif a[0] == SHIFT:# or len(list1) == 1:
            parserstate.list1 = list1+list2+[buf[0]]
            parserstate.list2 = [];
            parserstate.buf = buf[1:]
        elif a[0] == NOARC:
	    n = len(list1)-1
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
          
        self._preparetransitionset(parserstate)

    def goldtransition(self, parserstate, goldrels=None):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        goldrels = goldrels or parserstate.goldrels
        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        head = parserstate.head

        r = buf[0]
        addedArc = False
        noleftchildren = True
        for x in list1:
            if x in goldrels[r]:
                noleftchildren = False
                break    
        
        
        norighthead = True
        for x in list1:
            if r in goldrels[x]:
                norighthead = False
                break
        
        
        
        if len(list1) == 0:
            a = (SHIFT, -1, -1)
            return a
            
        
        l = list1[len(list1)-1]     
        if l in goldrels[r]:
            rel = goldrels[r][l]
            a = (LEFTARC, 0, rel)
        elif r in goldrels[l]:
            rel = goldrels[l][r]
            a = (RIGHTARC, 0, rel)
        elif norighthead and noleftchildren:
            a = (SHIFT, -1, -1)
        else:
            a = (NOARC, 0, 1)
        return a

    def trans_to_str(self, t, state, pos, fpos=None):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        if t[0] == SHIFT:
            if fpos is None:
                return "Shift\t%s" % (pos[state.buf[0]])
            else:
                return "Shift\t%s\t%s" % (pos[state.buf[0]], fpos[state.buf[0]])
        elif t[0] == LEFTARC:
            return "Left-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        elif t[0] == RIGHTARC:
            return "Right-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        elif t[0] == NOARC:
            #return "NoArc"
            return "NoArc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])

    @classmethod
    def trans_from_line(self, line):
        if line[0] == 'Left-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Right-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Shift':
            fields = { 'action':line[0], 'pos':line[1] }
            if len(line) > 2:
                fields['fpos'] = line[2]
        elif line[0] == 'NoArc':
            #fields = { 'action':line[0] }
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }        
        else:
            raise ValueError(line[0])
        return fields
    

    def tuple_trans_to_int(self, cand, t):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])

        base = 0
        
        if t[0] == SHIFT:
            return 0
        
        if cand[0][0] == SHIFT:
            base = 1
        
        if t[0] == NOARC:
            return base + t[2]
            
        if len(cand) > 1 and cand[1][0] == NOARC:
            base += RELS    

        if t[0] == LEFTARC:
            return base + t[1]*RELS + t[2]
        
        if len(cand) > 2 and cand[2][0] == LEFTARC:
            base += RELS
        
        if t[0] == RIGHTARC:
            return base + t[1]*RELS + t[2]
            
            

    def tuple_trans_from_int(self, cand, action):
        
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        RELS = len(self.mappings['rel'])
        rel = -1
                
                
        if cand[0][0] == SHIFT:
            if action == 0:
                a = cand[0]
            else:
                a = cand[(action - 1) / RELS + 1]
                rel = (action - 1) % RELS
        else:
            a = cand[action / RELS]
            rel = action % RELS       

        return a, rel



class Covington3(TransitionSystem):
    @classmethod
    def actions_list(self):
        return [ 'Shift', 'NoArc', 'Left-Arc', 'Right-Arc']

    def create_cycles(self, parserstate, h, d):
        head = parserstate.head
        n = h
        
        if n == d:
            return True 
        
        while n > 0:
            n = head[n][0]
            if n == d:
                return True 
        return False

    def _preparetransitionset(self, parserstate):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        
        list1, list2, buf, head = parserstate.list1, parserstate.list2, parserstate.buf, parserstate.head

        t = []
        
        if len(buf) != 0:
            
            if len(list1) == 0:
                t += [(SHIFT, -1)]
            else:  
                t += [(SHIFT, -1)]
                t += [(NOARC, 0)]
                        
                for si in xrange(len(list1)):
                    n = len(list1)-1
                    li = n - si
                    if si == 3:
                        break
                    if list1[li] != 0 and head[list1[li]][0] < 0 and not self.create_cycles(parserstate, head[buf[0]][0], list1[li]):
                        t += [(LEFTARC, si)]
                    
                for si in xrange(len(list1)):
                    n = len(list1)-1
                    li = n - si
                    if si == 3:
                        break
                    
                    if head[buf[0]][0] < 0 and not self.create_cycles(parserstate, head[list1[li]][0], buf[0]):
                        t += [(RIGHTARC, si)]
                
        
        
        parserstate._transitionset = t
    
    
        
    def advance(self, parserstate, action):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        RELS = len(self.mappings['rel'])
        cand = parserstate.transitionset()

       
         
        if isinstance(action, int):
           a, rel = self.tuple_trans_from_int(cand, action)
        else:
           rel = action[-1]
           a = action[:-1]

        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
  
        
        if a[0] == LEFTARC:
            n = len(list1)-1
            si = a[1] 
            parserstate.head[list1[n-si]] = [buf[0], rel]
            parserstate.list2 = list1[(n-si):]+list2
            parserstate.list1 = list1[:(n-si)]
        elif a[0] == RIGHTARC:
            n = len(list1)-1
            si = a[1]
            parserstate.head[buf[0]] = [list1[n-si], rel]
            parserstate.list2 = list1[(n-si):]+list2
            parserstate.list1 = list1[:(n-si)]
        
        elif a[0] == SHIFT:
            parserstate.list1 = list1+list2+[buf[0]]
            parserstate.list2 = [];
            parserstate.buf = buf[1:]
        elif a[0] == NOARC:
            n = len(list1)-1
            parserstate.list2 = [list1[n]]+list2
            parserstate.list1 = list1[:n]
        self._preparetransitionset(parserstate)

    def goldtransition(self, parserstate, goldrels=None):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        

        goldrels = goldrels or parserstate.goldrels
        list1 = parserstate.list1
        list2 = parserstate.list2
        buf = parserstate.buf
        head = parserstate.head

        r = buf[0]
        addedArc = False
        noleftchildren = True
        for x in list1:
            if x in goldrels[r]:
                noleftchildren = False
                break    
        
        
        norighthead = True
        for x in list1:
            if r in goldrels[x]:
                norighthead = False
                break
        
        
        
        if len(list1) == 0:
            a = (SHIFT, -1, -1)
            return a
            
      
        l = list1[len(list1)-1]     
        if l in goldrels[r]:
            rel = goldrels[r][l]
            a = (LEFTARC, 0, rel)
        
        elif r in goldrels[l]:
            rel = goldrels[l][r]
            a = (RIGHTARC, 0, rel)
        
        elif l-1 >= 0 and l-1 in goldrels[r]:
            rel = goldrels[r][l-1]
            a = (LEFTARC, 1, rel)
            
        elif l-1 >= 0 and r in goldrels[l-1]:
            rel = goldrels[l-1][r]
            a = (RIGHTARC, 1, rel)
                
        elif l-2 >= 0 and l-2 in goldrels[r]:
            rel = goldrels[r][l-2]
            a = (LEFTARC, 2, rel)
        
        elif l-2 >= 0 and r in goldrels[l-2]:
            rel = goldrels[l-2][r]
            a = (RIGHTARC, 2, rel)
        elif norighthead and noleftchildren:
            a = (SHIFT, -1, -1)
        else:
            a = (NOARC, 0, 1)
        return a

    def trans_to_str(self, t, state, pos, fpos=None):
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        if t[0] == SHIFT:
            if fpos is None:
                return "Shift\t%s" % (pos[state.buf[0]])
            else:
                return "Shift\t%s\t%s" % (pos[state.buf[0]], fpos[state.buf[0]])
        elif t[0] == LEFTARC:
            return "Left-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        elif t[0] == RIGHTARC:
            return "Right-Arc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])
        elif t[0] == NOARC:
            #return "NoArc"
            return "NoArc\t%d\t%s" % (t[1]+1, self.invmappings['rel'][t[2]])

    @classmethod
    def trans_from_line(self, line):
        if line[0] == 'Left-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Right-Arc':
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }
        elif line[0] == 'Shift':
            fields = { 'action':line[0], 'pos':line[1] }
            if len(line) > 2:
                fields['fpos'] = line[2]
        elif line[0] == 'NoArc':
            #fields = { 'action':line[0] }
            fields = { 'action':line[0], 'n':int(line[1]), 'rel':line[2] }        
        else:
            raise ValueError(line[0])
        return fields
    
     
    def tuple_trans_to_int(self, cand, t, num_la=0, num_ra=0,num_la_total=0):
        SHIFT = self.mappings['action']['Shift']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        NOARC = self.mappings['action']['NoArc']
        

        RELS = len(self.mappings['rel'])

        base = 0
        if t[0] == SHIFT:
            return 0

        if cand[0][0] == SHIFT:
            base = 1
                        
        if t[0] == NOARC:
            return base + t[2]
            
        if len(cand) > 1 and cand[1][0] == NOARC:
            base += RELS 

        if t[0] == LEFTARC:
            return base + num_la*RELS + t[2]
        
        

        if t[0] == RIGHTARC:
            return base + num_la_total*RELS + num_ra*RELS + t[2]
        
    def tuple_trans_from_int(self, cand, action):
        
        SHIFT = self.mappings['action']['Shift']
        NOARC = self.mappings['action']['NoArc']
        LEFTARC = self.mappings['action']['Left-Arc']
        RIGHTARC = self.mappings['action']['Right-Arc']
        RELS = len(self.mappings['rel'])
        rel = -1
        
        if cand[0][0] == SHIFT:
            if action == 0:
                a = cand[0]
            else:
                a = cand[(action - 1) / RELS + 1]
                rel = (action - 1) % RELS
        else:
            a = cand[action / RELS]
            rel = action % RELS       

        return a, rel

