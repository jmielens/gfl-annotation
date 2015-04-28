#!/usr/bin/python

import sys, re, os, codecs, json, copy
from Tkinter import *
from optparse import OptionParser
sys.path.insert(0, "..")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gflparser'))
import gfl_parser

class GFL_Anno(Frame):
  
    def __init__(self, parent, sentences):
        Frame.__init__(self, parent, background="grey")   
         
        self.parent = parent
        self.sentences = sentences
        self.annotations = [[sentence] for sentence in self.sentences]
        self.sentenceIndex = -1
        
        self.initUI()

    def dumpAnnotations(self):
        print "Dumping Annotations"
        f = open(options.outputFile,'w')
        for anno in self.annotations:
            f.write(anno[-1]+"\n")
        f.close()

    def onBracketButtonPress(self,editingBox):
        editingBox.insert(SEL_FIRST, "(")
        editingBox.insert(SEL_LAST, ")")
        bracket = self.gflEdit.get(SEL_FIRST, SEL_LAST)
        self.gflEdit.insert(END, "\n\n("+bracket+")")

    def checkGFL(self):
        currentAnnotation = self.gflEdit.get(1.0,END)
        self.config(bg="grey")
        self.sentenceDisplay.config(bg="grey")
        print "Checked GFL"
        try:
            self.annotations[self.sentenceIndex].append(currentAnnotation)
            parse = gfl_parser.parse(self.rawSentence.get().split(), currentAnnotation, check_semantics=True)
        except Exception, e:
            print "GFL Error!"
            self.config(bg="red")
            self.sentenceDisplay.config(bg="red")
            return False

        print self.annotations
        return True
        

    def undoAnnotation(self):
        print "Undo-ing Last Annotation"
        self.config(bg="grey")
        self.sentenceDisplay.config(bg="grey")
        self.annotations[self.sentenceIndex] = self.annotations[self.sentenceIndex][:-1]
        self.gflEdit.delete(1.0, END)
        self.gflEdit.insert(END,self.annotations[self.sentenceIndex][-1])

    def changeSentence(self,next):
        self.config(bg="grey")
        self.sentenceDisplay.config(bg="grey")
        good = True
        if self.sentenceIndex > -1:
            good = self.checkGFL()

        if not good:
            return
            
        if next:
            if (self.sentenceIndex+1 < len(self.sentences)):
                self.sentenceIndex += 1
                self.rawSentence.set(self.sentences[self.sentenceIndex])
                self.gflEdit.delete(1.0, END)
                self.gflEdit.insert(END,self.annotations[self.sentenceIndex][-1])
                print "Next Sentence..."
        else:
            if (self.sentenceIndex > 0):
                self.sentenceIndex -= 1
                self.rawSentence.set(self.sentences[self.sentenceIndex])
                self.gflEdit.delete(1.0, END)
                self.gflEdit.insert(END,self.annotations[self.sentenceIndex][-1])
                print "Previous Sentence..."
    
    def initUI(self):
      
        self.parent.title("GFL Annotation Interface")
        self.pack(fill=BOTH, expand=1)

        self.rawSentence = StringVar()
        

        # Build Sentence Display Area
        self.sentenceDisplay = Label(self, font=("Helvetica",16), bg="grey", textvariable=self.rawSentence)
        self.sentenceDisplay.pack(side=TOP,padx=10,pady=10)
        self.rawSentence.set("GFL Annotation System")

        # Frame Packing
        editingFrame = Frame(self, relief=RAISED, borderwidth=1)
        cmdButtonFrame = Frame(editingFrame, borderwidth=1)
        editingFrame.pack(fill=BOTH, expand=1)
        cmdButtonFrame.pack(fill=X, expand=0)

         
        # Command Tray
        checkButton = Button(cmdButtonFrame, text="Check", command=self.checkGFL)
        undoButton = Button(cmdButtonFrame, text="Undo", command=self.undoAnnotation)
        prevButton = Button(cmdButtonFrame, text="Prev", command=lambda:self.changeSentence(False))
        nextButton = Button(cmdButtonFrame, text="Next", command=lambda:self.changeSentence(True))
        bracketButton = Button(cmdButtonFrame, text="Bracket", command=lambda:self.onBracketButtonPress(self.gflEdit))
        checkButton.pack(side=LEFT,padx=(375,5),pady=5)
        undoButton.pack(side=LEFT,padx=5,pady=5)
        bracketButton.pack(side=LEFT,padx=100,pady=5)
        prevButton.pack(side=LEFT,padx=5,pady=5)
        nextButton.pack(side=LEFT,padx=5,pady=5)

        # Edit Box
        self.gflEdit = Text(editingFrame)
        self.gflEdit.insert(END,"Press the 'Next' button to begin...")
        self.gflEdit.pack()


def main():

    sentences = [line.strip() for line in open(options.sentenceFile)]

    root = Tk()
    root.geometry("1300x700+100+100")
    app = GFL_Anno(root,sentences)
    
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Dump Annotations...", command=app.dumpAnnotations)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    root.mainloop()  


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-s", "--sentences", dest="sentenceFile",
                  help="Location of sentences to annotate, one sentence per line")
    parser.add_option("-o", "--output", dest="outputFile",
                  help="Location of JSON output file")
    parser.set_defaults(outputFile="out")
    (options, args) = parser.parse_args()

    main() 