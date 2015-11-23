#!/usr/bin/python

import sys, re, os, codecs, json, copy, time
from Tkinter import *
from optparse import OptionParser
from nltk.tokenize.stanford import StanfordTokenizer
sys.path.insert(0, "..")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gflparser'))
import gfl_parser


def subscript_add(sentenceList):

    for wType in set(sentenceList):
        if sentenceList.count(wType) > 1:
            sentIndex = 0
            count = 1
            for word in sentenceList:
                if word == wType:
                    sentenceList[sentIndex] = word+"~"+str(count)
                    count += 1
                sentIndex += 1

    return sentenceList

class GFL_Anno(Frame):
  
    def __init__(self, parent, sentences):
        Frame.__init__(self, parent, background="grey")   
         
        self.parent = parent
        self.sentences = sentences
        self.annotations = [[sentence.replace(u'\xa0', u' ')] for sentence in self.sentences]
        self.sentenceIndex = -1
        
        self.initUI()

    def dumpAnnotations(self):
        #print "Dumping Annotations"
        f = codecs.open(options.outputFile,'w','utf-8')
        for index, anno in enumerate(self.annotations):
            jsonLine = """{"comment":"","last":false,"number":"""
            jsonLine += str(index)
            jsonLine += ""","submitted":["""
            jsonLine += str(int(time.time()))
            jsonLine += """],"pos":null,"anno":" """
            jsonLine += anno[-1].replace("\n", "\\n")
            jsonLine += """ ","user":null,"analyzed":["""
            jsonLine += str(int(time.time()))
            jsonLine += """],"accessed":["""
            jsonLine += str(int(time.time()))
            jsonLine += """],"dataset":"null","id":"0","sent":" """
            jsonLine += anno[0].replace("\n", "\\n")
            jsonLine += """ ","userAdd":false}"""
            f.write(jsonLine+u"\n")
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
        #print "Checked GFL"
        try:
            self.annotations[self.sentenceIndex].append(currentAnnotation)
            print currentAnnotation,self.rawSentence.get().split()
            parse = gfl_parser.parse(self.rawSentence.get().split(), currentAnnotation, check_semantics=True)
        except Exception, e:
            #print "GFL Error!"
            self.config(bg="red")
            self.sentenceDisplay.config(bg="red")
            return False

        return True
        

    def undoAnnotation(self):
        #print "Undo-ing Last Annotation"
        if len(self.annotations[self.sentenceIndex]) > 1:
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
                #print "Next Sentence..."
        else:
            if (self.sentenceIndex > 0):
                self.sentenceIndex -= 1
                self.rawSentence.set(self.sentences[self.sentenceIndex])
                self.gflEdit.delete(1.0, END)
                self.gflEdit.insert(END,self.annotations[self.sentenceIndex][-1])
                #print "Previous Sentence..."

        self.parent.title("GFL Annotation Interface - "+str(self.sentenceIndex+1))
    
    def initUI(self):
      
        self.parent.title("GFL Annotation Interface")
        self.pack(fill=BOTH, expand=1)

        self.rawSentence = StringVar()
        

        # Build Sentence Display Area
        self.sentenceDisplay = Label(self, font=("Helvetica",12), bg="grey", textvariable=self.rawSentence)
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
        self.gflEdit = Text(editingFrame,width=120,wrap=WORD)
        self.gflEdit.insert(END,"Press the 'Next' button to begin...")
        self.gflEdit.pack()


def main():

    tokenizer = StanfordTokenizer(path_to_jar=os.path.dirname(os.path.realpath(__file__))+"/stanford-postagger.jar")

    if options.sentenceFile != "":
        if options.sentenceFile.endswith("conll"):
            sentences = [" ".join(subscript_add([line.split("\t")[1] for line in rawSentence.split("\n") if len(line.split("\t")) > 4 and line.split("\t")[3] != "."])) for rawSentence in open(options.sentenceFile).read().split("\n\n")]
            sentences = [s for s in sentences if len(s.split(" ")) <= options.maxLength]
        else:
            sentences = [line.strip() for line in open(options.sentenceFile)]
    else:
        jFile = open(options.jsonSentsFile)
        sentences = [sent['clean'] for sent in json.load(jFile)]
        jFile.close()

    if options.tokenize:
        newSents = []
        for sent in sentences:
            toks = tokenizer.tokenize(sent)
            for tok in toks:
                if toks.count(tok) > 1:
                    for num in range(1,toks.count(tok)+1):
                        toks[toks.index(tok)] = tok+"~"+str(num)
            newSents.append(u" ".join(toks))
        sentences = newSents
    else:
        newSents = []
        for sent in sentences:
            toks = [tok.decode('utf-8') for tok in sent.split()]
            newSents.append(u" ".join(toks))
        sentences = newSents

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
    parser.add_option("-j", "--jsonSents", dest="jsonSentsFile",
                  help="Location of sentences to annotate, JSON format")
    parser.add_option("-t", "--tokenize", dest="tokenize", action="store_true",
                  help="Tokenize input sentences")
    parser.add_option("-o", "--output", dest="outputFile",
                  help="Location of JSON output file")
    parser.add_option("-l", "--length", dest="maxLength",
                  help="Maximum Sentence Length")
    parser.set_defaults(outputFile="out.json",sentenceFile="",maxLength=30)
    (options, args) = parser.parse_args()

    main() 