try:
    import speech_recognition as sr
except: paass      

from threading import Thread

from .evbase import Event
from .events import SpeechEvent

class Thesaurus():
    def __init__(self):
        self.words = dict()
        self.add_homophones('cozmo', \
                            ["cozimo","cosimo","cosmo", \
                             "kozmo","cosmos","cozmos"])
        self.add_homophones('right', ['write','wright'])
        self.add_homophones('1',['one','won'])
        self.add_homophones('cube1',['q1','coupon','cuban'])
        self.phrase_tree = dict()
        self.add_phrases('cube1',['cube 1'])
        self.add_phrases('cube2',['cube 2'])
        self.add_phrases('cube3',['cube 3'])
        self.add_phrases('paperclip',['paper clip'])
        self.add_phrases('deli-slicer',['deli slicer'])
        

    def add_homophones(self,word,homophones):
        if not isinstance(homophones,list):
            homophones = [homophones]
        for h in homophones:
            self.words[h] = word

    def lookup_word(self,word):
        return self.words.get(word,word)

    def add_phrases(self,word,phrases):
        if not isinstance(phrases,list):
            phrases = [phrases]
        for phrase in phrases:
            wdict = self.phrase_tree
            for pword in phrase.split(' '):
                wdict[pword] = wdict.get(pword,dict())
                wdict = wdict[pword]
            wdict[''] = word

    def substitute_phrases(self,words):
        result = []
        while words != []:
            word = words[0]
            del words[0]
            wdict = self.phrase_tree.get(word,None) 
            if wdict is None:
                result.append(word)
                continue
            prefix = [word]
            while words != []:
                wdict2 = wdict.get(words[0],None)
                if wdict2 is None: break
                prefix.append(words[0])
                del words[0]
                wdict = wdict2
            subst = wdict.get('',None)
            if subst is not None:
              result.append(subst)
            else:
              result = result + prefix
        return result

class SpeechListener():
  def __init__(self,robot,thesaurus):
    self.robot = robot
    self.thesaurus = thesaurus

  def speech_listener(self):
    self.rec = sr.Recognizer()
    with sr.Microphone() as source:
      while True:
          audio = self.rec.listen(source)
          try:
              utterance = self.rec.recognize_google(audio).lower()
              words = [self.thesaurus.lookup_word(w) for w in utterance.split(" ")]
              words = self.thesaurus.substitute_phrases(words)
              string = " ".join(words)
              print("Heard: '%s'" % string)
              evt = SpeechEvent(string,words)
              self.robot.erouter.post(evt)
          except sr.RequestError as e:
              print("Could not request results form google speech recognition service; {0}".format(e)) 
          except: pass

  def start(self):
    self.thread = Thread(target=self.speech_listener)
    self.thread.daemon = True #ending fg program will kill bg program
    self.thread.start()