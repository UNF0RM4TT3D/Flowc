#!/bin/python3
import xml.etree.ElementTree as ET
import sys

class Decomp():
    def __init__(self,filename):
        self.tagdict = {
                'function' : self.function,
                'declare' : self.declare,
                'input' : self.input,
                'assign' : self.assign,
                'output' : self.output,
                'if' : self._if_,
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
                'call' : self.call,
                'comment' : self.comment

                }
        self.tree = ET.parse(filename)
        self.root = self.tree.getroot()
        self.outbuffer = ""
        self.indentlevel = 0
        if self.root.tag != 'flowgorithm':
            print(self.root.tag, self.root.attrib)
            print("Error: Not a flowgorithm file")
            sys.exit(1)
    
    def indent(self):
        ind = "     "
        out = ""
        for i in range(self.indentlevel):
            out += ind
        return(out)

    def comment(self,root):
        lines = root.attrib['text'].splitlines()
        if len(lines) == 1:
            self.outbuffer += self.indent() + "// " + root.attrib['text'] + "\n"
        else:
            self.outbuffer += self.indent() + "/*\n"
            for l in lines:
                self.outbuffer += self.indent() + l + "\n"
            self.outbuffer += self.indent() + "*/\n"

    def call(self, root):
        self.outbuffer += self.indent() + "call(" + root.attrib['expression'] + ")\n"

    def write(self, root):
        self.outbuffer += self.indent() + "write(" + root.attrib['expression'] + ")\n"

    def close(self, root):
        self.outbuffer += self.indent() + "close()\n"

    def open(self, root):
        self.outbuffer += self.indent() + "open(" + root.attrib['expression'] + ", " + root.attrib['mode'] + ")\n"

    def read(self, root):
        self.outbuffer += self.indent() + "read(" + root.attrib['variable'] + ")\n"

    def home(self, root):
        self.outbuffer += self.indent() + "home()\n"

    def forward(self, root):
        self.outbuffer += self.indent() + "forward(" + root.attrib['expression'] + ", " + root.attrib['pen'] + ")\n"

    def turn(self, root):
        self.outbuffer += self.indent() + "turn(" + root.attrib['expression'] + ", " + root.attrib['rotate'] + ")\n"

    def _for_(self, root):
        self.outbuffer += self.indent() + "for (" + root.attrib['variable'] + "; " + root.attrib['start'] + "; " + root.attrib['end'] + "; " + root.attrib['direction'] + "; " + root.attrib['step'] + ") {\n" #}for autoindent breaking in some editors
        self.indentlevel += 1
        self.decomp(root)
        self.indentlevel -= 1
        self.outbuffer += self.indent() + "} \n"

    def _do_(self, root):
        self.outbuffer += self.indent() + "do (" + root.attrib['expression'] + ") {\n" #}for autoindent breaking in some editors
        self.indentlevel += 1
        self.decomp(root)
        self.indentlevel -= 1
        self.outbuffer += self.indent() + "} \n"

    def _while_(self, root):
        self.outbuffer += self.indent() + "while (" + root.attrib['expression'] + ") {\n" #}for autoindent breaking in some editors
        self.indentlevel += 1
        self.decomp(root)
        self.indentlevel -= 1
        self.outbuffer += self.indent() + "} \n"

    def _if_(self, root):
        self.outbuffer += self.indent() + "if (" + root.attrib['expression'] + ") {\n" #}for autoindent breaking in some editors
        self.indentlevel += 1
        self.decomp(root[0])
        self.indentlevel -= 1
        self.outbuffer += self.indent() + "} \n"
        if root[1]:
            self.outbuffer += self.indent() + "else {\n" #}
            self.indentlevel += 1
            self.decomp(root[1])
            self.indentlevel -= 1
            self.outbuffer += self.indent() + "} \n"

    def output(self, root):
        if root.attrib['newline'] == "True":
            self.outbuffer += self.indent() + "outln(" + root.attrib['expression'] + ")\n"
        else:
            self.outbuffer += self.indent() + "output(" + root.attrib['expression'] + ")\n"

    def assign(self, root):
        self.outbuffer += self.indent() + root.attrib['variable'] + " = " + root.attrib['expression'] + "\n"

    def input(self, root):
        self.outbuffer += self.indent() + "input(" + root.attrib['variable'] + ")\n"

    def declare(self, root):
        self.outbuffer += self.indent() + root.attrib['type'] + " " + root.attrib['name']
        if root.attrib['array'] == "True":
            self.outbuffer +="[" + root.attrib['size'] + "]"
        self.outbuffer +="\n"

    def function(self, root):
        params = ""
        self.outbuffer +="func " + root.attrib['name'] + "(" #)for autoindent breaking in some editors
        for parameter in root[0]:
            if params != "":
                params = params + ", "
            params = params + parameter.attrib['type'] + " " + parameter.attrib['name']
            if parameter.attrib['array'] == 'True':
                params = params +"[]"
        self.outbuffer +=params +") {\n" #} for autoindent breaking in some editors
        self.indentlevel += 1
        self.decomp(root)
        self.indentlevel -= 1
        self.outbuffer +="} \n"

    def decomp(self, root=None):
        if root == None:
            root = self.root
        for child in root:
            if child.tag in self.tagdict:
                action = self.tagdict[child.tag]
                action(child)
            else:
                self.decomp(child)

if __name__=='__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} INPUT_FILE OUTPUT_FILE")
        sys.exit(1)
    print(sys.argv[1])
    d = Decomp(sys.argv[1])
    d.decomp()
    print(d.outbuffer, file=open(sys.argv[2], mode='w'))
