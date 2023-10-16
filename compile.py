#!/bin/python3
import xml.etree.ElementTree as ET
import sys

class Comp:
    def __init__(self, filename):
        with open(filename, mode='r') as source:
            self.source = source.read().splitlines()
        self.tagdict = {
                'func' : self.function,
                'input': self.input,
                'output' : self.output,
                'outln' : self.outln, #{ Autointend breaks without this
                '}' : self.clbracket,
                'if' : self._if_,
                'else' : self._else_,
                'else{' : self._else_, #}
                'while' : self._while_,
                'do' : self._do_,
                'for' : self._for_,
                'turn' : self.turn,
                'forward' : self.forward,
                'home' : self.home,
                'read' : self.read,
                'open' : self.open,
                'close' : self.close,
                'write' : self.write,
                'call' : self.call
                }
        self.definitions = {'Integer', 'String', 'Real', 'Boolean'}
        self.elements = [ET.Element('flowgorithm')]
        self.elements[0].attrib = {'fileversion' : '3.0'}
        self.parents = [self.elements[0]]
        self.brackets = []
        self.lastclosed = None
        print(self.source, )

    def comment(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'comment'))
        self.elements[-1].attrib = { 'text' : line.lstrip('/')}

    def call(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'call'))
        attr = line.strip().lstrip('call (').removesuffix(')')
        self.elements[-1].attrib = { 'expression' : attr}

    def write(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'write'))
        attr = line.strip().lstrip('write (').rstrip(')')
        self.elements[-1].attrib = { 'expression' : attr}

    def close(self, line):
        if line.strip().removeprefix('close()') != "":
            print(line,"[WARNING] close() doesn't take arguments, ignoring")
        self.elements.append(ET.SubElement(self.parents[-1],'close'))

    def open(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'open'))
        attr = line.strip().lstrip('open (').rstrip(')').split(',')
        if len(attr) !=2:
            print(line, "open() expects exactly 2 arguments")
        self.elements[-1].attrib = { 'expression' : attr[0], 'mode' : attr[1]}

    def read(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'read'))
        attr = line.strip().lstrip('read (').rstrip(')')
        self.elements[-1].attrib = { 'variable' : attr}

    def home(self, line):
        if line.strip().removeprefix('home()') != "":
            print(line,"[WARNING] home() doesn't take arguments, ignoring")
        self.elements.append(ET.SubElement(self.parents[-1],'home'))

    def forward(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'forward'))
        attr = line.strip().lstrip('forward (').rstrip(')').split(',')
        if len(attr) !=2:
            print(line, "forward() expects exactly 2 arguments")
        self.elements[-1].attrib = { 'expression' : attr[0], 'pen' : attr[1]}

    def turn(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'turn'))
        attr = line.strip().lstrip('turn (').rstrip(')').split(',')
        if len(attr) !=2:
            print(line, "turn() expects exactly 2 arguments")
        self.elements[-1].attrib = { 'expression' : attr[0], 'rotate' : attr[1]}

    def _for_(self, line):
        if line.rstrip().endswith('}'):
            print(line, "Translator doesn't support single line for expressions")
            sys.exit(1)
        exp = line.strip().strip('for {')[1:-1].split(';') #}
        if len(exp) != 5:
            print(line, "for loops expect 5 arguments separated by ;")
            sys.exit(1)
        self.elements.append(ET.SubElement(self.parents[-1],'for'))
        self.elements[-1].attrib = { 'variable' : exp[0], 'start' : exp[1], 'end' : exp[2], 'direction' : exp[3], 'step' : exp[4], } 
        self.parents.append(self.elements[-1])

    def _do_(self, line):
        if line.rstrip().endswith('}'):
            print(line, "Translator doesn't support single line do expressions")
            sys.exit(1)
        exp = line.strip().strip('do {')[1:-1] #}
        self.elements.append(ET.SubElement(self.parents[-1],'do'))
        self.elements[-1].attrib = { 'expression' : exp} 
        self.parents.append(self.elements[-1])

    def _while_(self, line):
        if line.rstrip().endswith('}'):
            print(line, "Translator doesn't support single line while expressions")
            sys.exit(1)
        exp = line.strip().strip('while {')[1:-1] #}
        self.elements.append(ET.SubElement(self.parents[-1],'while'))
        self.elements[-1].attrib = { 'expression' : exp} 
        self.parents.append(self.elements[-1])

    def _else_(self,line):
        if len(line.split()) !=1 and line.split()[1] == 'if':
            print(line,'else if on one line not supported by translator')
            sys.exit(1)
        if self.lastclosed != None:
            if self.lastclosed.tag == 'if':
                self.parents.append(self.lastclosed[1])
        else:
            print(line,'{ not closed, expected: }')
            sys.exit(1)

    def _if_(self, line):
        if line.rstrip().endswith('}'):
            print(line, "Translator doesn't support single line if expressions")
            sys.exit(1)
        exp = line.strip().strip('if {')[1:-1] #}
        self.elements.append(ET.SubElement(self.parents[-1],'if'))
        self.elements[-1].attrib = { 'expression' : exp}
        self.brackets.append(self.elements[-1])
        self.elements.append(ET.SubElement(self.elements[-1],'then'))
        self.parents.append(self.elements[-1])
        self.elements.append(ET.SubElement(self.elements[-2],'else'))

    def clbracket(self, line):
        if not line.strip().endswith('}'):
            print('Unexepected statements after }')
            sys.exit(1)
        if len(self.brackets) != 0:
            self.lastclosed = self.brackets.pop()
        else:
            self.lastclosed = None
        if self.parents[-1] == self.elements[0]:
            print("end of function")
        if len(self.parents) == 0:
            print('Something weird has happened (misplaced })')
            sys.exit(1)
        self.parents.pop()

    def outln(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'output'))
        self.elements[-1].attrib = { 'expression' : line.rstrip(')').split('(')[1], 'newline' : "True"}

    def output(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'output'))
        self.elements[-1].attrib = { 'expression' : line.rstrip(')').split('(')[1], 'newline' : "False"}

    def input(self, line):
        self.elements.append(ET.SubElement(self.parents[-1],'input'))
        self.elements[-1].attrib = { 'variable' : line.rstrip(')').split('(')[1]}

    def assignment(self, line):
        exp = line.strip().split('=')
        self.elements.append(ET.SubElement(self.parents[-1],'assign'))
        self.elements[-1].attrib = { 'variable' : exp[0].strip(), 'expression' : exp[1].strip()}

    def declare(self,line):
        words = line.removeprefix(line.strip().split()[0] + ' ').split(',')
        array = words[1].endswith(']')
        name = words[1].split('[') #]
        name.append("")
        self.elements.append(ET.SubElement(self.parents[-1],'declare'))
        self.elements[-1].attrib = { 'name' : name[0], 'type' : words[0], 'array' : str(array), 'size' : name[1].strip(']')}

    def function(self, line):
        if not line.endswith('{') : #}
            print(line,"<<< expected { after function declaration") #}
            sys.exit(1)
        self.elements.append(ET.SubElement(self.elements[0],'function'))
        root = self.elements[-1]
        func = line.split('(') # )
        name = func[0].split()[1]
        args = func[1].split(')')[0].split(',')
        self.parents.append(self.elements[-1])
        root.attrib = { 'name' : name, 'type' : "None", 'variable' : "" }
        self.elements.append(ET.SubElement(root, 'parameters'))
        parm = self.elements[-1] #reference to the parameters object
        for a in args:
            arg = a.split()
            if arg == []:
                break
            array = str(arg[1].endswith('[]')) #is an array?
            self.elements.append(ET.SubElement(parm, 'parameter'))
            self.elements[-1].attrib = { 'name' : arg[1].strip('[]'), 'type' : arg[0], 'array' : array } 
        self.elements.append(ET.SubElement(root, 'body'))
        self.parents.append(self.elements[-1])

    def compile(self, root=None):
        if root == None:
            root = self.elements[0]
        for line in self.source:
            words = line.strip().split()
            calls = line.strip().split('(') #)
            print('line',line)
            print('parents',self.parents)
            if len(words) == 0 or len(calls) == 0:
                print("no line")
                continue
            elif line.strip().startswith("//"):
                self.comment(line)
            elif words[0] in self.tagdict:
                print("keyword")
                action = self.tagdict[words[0]]
                action(line)
            elif words[0] in self.definitions:
                print("declaration")
                self.declare(line)
            elif calls[0] in  self.tagdict:
                print("call")
                action = self.tagdict[calls[0]]
                action(line)
            elif len(line.split('=')) > 1:
                print("assignment")
                self.assignment(line)
            else:
                print(line,"Not recognised, ignoring")


if __name__=='__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} INPUT_FILE OUTPUT_FILE")
        sys.exit(1)
    c = Comp(sys.argv[1])
    c.compile()
    tree = ET.ElementTree(c.elements[0])
    ET.indent(tree)
    tree.write(sys.argv[2])
