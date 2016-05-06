
## Youtube Parser and Downloader
## Written and Devoloped by Chris J. Nguyen

import pafy, urllib, sys, os, re, time, random
import unicodedata

LINK = "llNuwhZWXKA"
SMALL = "https://www.youtube.com/watch?v=Ybo4QvKVHoE"

__version__ = "1.8.1"
__author__ = "Chris J. Nguyen"
__date__ = "April 6th, 2016"
__copyright__ = "(C) 2016-2018 Chris J. Nguyen. GNU GPL 3."

_Bricks = "~-"*16
_Fancy = "\n\n%s\n\n" % _Bricks

try:
    _ScriptLoc = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _ScriptLoc = os.path.dirname(os.path.abspath(sys.argv[0]))

class Tools():
    ## Tools for primary function
    
    def MakePath(self, path):
        ## Recursively creates path
        ## working back from the parent directory each iteration
        while True:
            try:
                if os.path.exists(path)==False:
                    os.mkdir(path)
                break
            except WindowsError:
                self.MakePath( os.path.join(path, "..") )

    def Slugify(self, String):
        ## Creates File appropriate ASCII file names
        Forbid = '[/:*?"<>|]'
        Frag = unicodedata.normalize('NFKD', String).encode('ascii','ignore')
        return re.sub(Forbid, "", Frag)

    def ReadFile(self, FileName, mode='rb'):
        with file(FileName, mode) as f:
            return f.read()
            
    def WriteFile(self, FileName, Content, mode='wb'):
        with file(FileName, mode) as f:
            f.write(Content)
        f.close()

    def Log(self, Content, Path="Log.txt", Start=""):
        stamp = str(time.asctime())
        stuff = Start + "\n%s \n%s" % (stamp, Content)
        self.WriteFile(Path, stuff, "a")

    def Convert(self, num, suffix='B'):
        ## Converts bytes
        ## http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    def Smart_Input(self, msg='(Y/N)'):
        ## raw_input() with additional system options
        while True:
            Out = raw_input(msg)
            OutUp = Out.upper()
            LOO = len(Out)
            if OutUp in "EXIT,SHIT,FUCK,QUIT,STOP" and len(Out)==4:
                raise SystemExit
            elif OutUp in ["LS", "DIR"]:
                print _Fancy, os.listdir('.')
            elif OutUp in ["GWD", "PWD"]:
                print _Fancy, os.getcwd()
            elif OutUp in ["FAQ", "HELP"]:
                print _Fancy, FAQ
            elif OutUp in ["START", "OPEN"]:
                os.startfile('.')
            else:
                return Out
            
    def Raw_Choice(self, Msg='(Y/N)', Options='YN', Length=1):
        ## Exactly what it sounds like...
        while True:
            Answer = self.Smart_Input(Msg+'> ').upper()
            if Answer in Options and len(Answer)==Length:
                return Answer
        
SAK = Tools()

class HTML():
    ## Class for parsing URLs and HTML
    
    def BruteTag(self, tag='href="/watch?v=', length=11, html=None, link=None):
        ## Finds opening tag "<class>"
        ## Returns list of all values in tags
        ## Primary method
        if html==None and link!=None:
            print "\nExtracting..."
            html = urllib.urlopen(link).read()
        values = []
        while True:
            a = html.find(tag)
            if a < 0: break
            b = a+len(tag)
            c = b+length
            val = html[ b : c ]
            html = html[c:]
            if val not in values:
                values.append ( str(val) )
        return values
            
    def Tag(self, tag="<a", html=None, link=None):
        ## Finds opening tag "<class>"
        ## Returns list of all values in tags
        return self.BruteTag(link = link)
    
        if html==None and link!=None:
            html = urllib.urlopen(link).read()
        html = html.decode("utf-8") #.encode("ascii")
        proto = re.compile(' data-vid="(.*?)"><')    ##(' href="/watch\?v=(.*?)"') ## Rule
        content = html #copy.deepcopy(html)
        values = []
        for snip in html.split(tag): #while True:
            val1 = content.find(tag)
            search = proto.search( snip ) #content[start:finish] )
            if search:
                main_val = search.group(1)
                if main_val not in values: values.append( main_val )
        return values

    def Download(self, Name, URL, Blocks=500000000):
        Content = urllib.urlopen(URL)
        Size = len( Content.read() )
        SAK.WriteFile(Name, "")
        print "\nDownloading and Writing: ", Name
        for x in xrange( (Size/Blocks)+1 ):
            SAK.WriteFile(Name, Content.read(Blocks), 'a' )

    def DownloadInst(self, inst, path):
        inst.download(path, True)
    
class Youtube(HTML):
    ## Primary class for handling YoutubeDL instances
    
    def GetURL(self, Link, Mode):
        ## Soon to be obsolete method for getting default DL URL
        ## Consoladate with Scrap Function
        obj = pafy.new(Link)

        if Mode == "VIDEO":
            inst = obj.getbest()
        elif Mode=="AUDIO":
            inst = obj.getbestaudio()
        else:
            self.UI()

        Name = inst.generate_filename()
        Size = inst.get_filesize()
        URL = inst.url
        return Name, Size, URL

    def Scrap(self, Link, Format="ALL"):
        ## Returns specific set of information about the video
        ## Notify dev if any Unicode Errors are raised
        obj = self.GetInst(Link)
        if Format=="ALL": inst = obj.getbest()
        elif Format=="AUDIO": inst = obj.getbestaudio()

        Cat = obj.category
        Views = obj.viewcount
        Plain = inst.generate_filename()
        title = SAK.Slugify( inst.title)
        Name = "%s - %s.%s" % ( title, obj.videoid, inst.extension )
        Size = inst.get_filesize()
        URL = inst.url
        return Views, Name, Size, URL, Cat, inst, Plain

class MassExtract(Youtube):
    ## Class used to extract video IDs from HTML
    ## and recusively download all associated
    def __init__(self, StartLink='', Loops=1, Active=True):
        SAK.MakePath("Youtube.com")
        if Active:
            if StartLink =='':
                StartLink = raw_input("\nEnter link >>> ")
                L = len(StartLink)
                if StartLink in "EXIT,QUIT,STOP,FUCK" and L==4:
                    sys.exit()
                if L==11:
                    StartLink = "https://www.youtube.com/watch?v=%s" % StartLink
                try: Loops = int(raw_input("Enter Loops >>> ")) + 1
                except ValueError:
                    print "\nWe need a number! Like 2, 3, 4, etc..."; return
            self.Run(StartLink, Loops)

    def Run(self, Link, Loops):
        ## Inputs a list and downloads all related videos
        ## Uses BruteTag function to get video IDs from raw HTML
        Select = Link
        print "\nRunning...", "\nExecuting %s iterations..." % Loops
        History = []; Related=['']
        for x in xrange(Loops):
            if True: #try:
                #

                for x in range(len(Related) ):
                    if len(Select)==11:
                        Select = "https://www.youtube.com/watch?v=%s" % Select
                    SelectTmp = Select
                    Related = self.Tag(link=Select)
                    if Select in History:
                        Select = random.choice(Related)
                    else: break
                
                
                History.append(Select)
                if x<=0:
                    Related = [Select] + Related
                print "\n\nFull List: \n%s\n" % Related
                Select = self.Parse(Related)
            #if True: #except ArithmeticError: # Exception as E:
                #print E; continue

    def Parse(self, MASS, Limit=2000000000):
        ## Parses video link a downlaods all related videos.
        ##Downlaods all videos in "MASS" list
        Most = 0; Select = ''
        print "\n\nAttempting to download %s items...\n" % len(MASS)
        for video in MASS:
            if True: #try:
                Views, Name, Size, URL, Cat, inst, Plain = self.Scrap(video)
                if Size > Limit: continue
                if Views > Most:
                    Most = Views; Select = video
                stringA = "Downloading: %s \nProcessing %s bytes..." % (Name, SAK.Convert( Size ))
                print "\n\n", stringA; SAK.Log(stringA, Start="\n\n")
                Path = os.path.join(_ScriptLoc, "Youtube.com", Cat, Name)
                #DirPath = os.path.join(_ScriptLoc, "Youtube.com", Cat)
                SAK.MakePath( os.path.dirname(Path) )
                if os.path.exists(Path):
                        print "Skipping...\n";
                        continue
                inst.download(Path, True)
                stringB = "Saved to: %s\n" % Path
                print stringB; SAK.Log(stringB)
        return Select

class User(Youtube):
    def __init__(self, Active=False):
        if Active:
            self.UI()
    def UI(self):
        ## Simply method for downloading single video
        while True:
            print "\n\na. Full Audio \t\tb. Full Video \nc. Exit \n" 
            choice = raw_input("(A/B/C) >>> ").upper()
            if len(choice) != 1: continue
            if choice in "AB":
                Mode = "AUDIO" if choice=="A" else "VIDEO"
                link = raw_input("\nEnter link or video ID > ")
                if len(link)==11:
                    link = "https://www.youtube.com/watch?v=%s" % link
                Name, Size, URL = self.GetURL(link, Mode)
                print "\nDownloading %s bytes..." % Size
                self.Download( Name, URL )
                print "\nSaved at: \n", os.path.join( os.getcwd(), Name)
            else: sys.exit()

if __name__ == "__main__":
    while True:
        if True: #try:
            print "\na. Manual Download \t\tb. Auto Download \nc. Exit"
            choice = SAK.Raw_Choice("(A/B/C) ", "ABC")
            if choice == "A": User(True)
            if choice == "B": Null = MassExtract()
            else: sys.exit()
        else: #except Exception as E:
            print "\n\n", E
            break
