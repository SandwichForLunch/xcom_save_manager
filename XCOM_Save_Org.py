import datetime
from pathlib import Path
import shutil
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
TABLE_NAME = 'xcomSaveStates'
engine = db.create_engine('sqlite:///%s.db' % TABLE_NAME, echo = True)
Session = sessionmaker(bind=engine)

def intTryParse(value):
    try:
        return int(value)
    except ValueError:
        return None

class Savestate(Base):
    #Save File
    #1 - Blah - Save Date
    #2 - save time
    #3 - save title
    #4 - mission 
    #5 - operation name
    #6 - game date
    #7 - game time
    __tablename__ = TABLE_NAME
    fileNum = db.Column(db.Integer, primary_key=True)
    mySaveNum = db.Column(db.Integer)
    saveDateTime = db.Column(db.DateTime)
    saveTitle = db.Column(db.String(50))
    mission = db.Column(db.String(50))
    operationName = db.Column(db.String(50))
    gameDateTime = db.Column(db.DateTime)
    filePath = db.Column(db.String(100))

    def __init__(self, file):
        print(file.name.split('\\'))

        while True:
            try:
                line1 = file.readline().replace('\n','')
                saveDate = line1[-11:].replace('\x00','').split('/')
                saveDate[0],saveDate[1],saveDate[2] = int(saveDate[2]), int(saveDate[0]), int(saveDate[1])
                break
            except:
                continue #just grab the next line

        line2 = file.readline().replace('\n','')
        saveTime = [*map(lambda x: int(x), line2.split(':'))]

        line3 = file.readline().replace('\n','')
        line4 = file.readline().replace('\n','')
        line5 = None
        if line4 != 'Geoscape':
            line5 = file.readline().replace('\n','')

        line6 = file.readline().replace('\n','')
        gameDate = line6.split('/')
        gameDate[0],gameDate[1],gameDate[2] = int(gameDate[2]), int(gameDate[0]), int(gameDate[1])

        line7 = file.readline().replace('\n','')
        gameTime = line7[:8].strip().split(' ')
        gameTime, ampm = [*map(lambda x: int(x), gameTime[0].split(':'))], gameTime[1]
        if ampm=='PM':
            gameTime[0] = gameTime[0] + 12 if gameTime[0] < 12 else gameTime[0]
        elif gameTime[0] == 12:
            gameTime[0] = 0

        #File Info
        self.filePath = file.name
        self.saveDateTime = datetime.datetime(*saveDate, *saveTime)
        
        #Game Info
        self.saveTitle = line3
        self.mission = line4
        self.operationName = line5
        self.gameDateTime = datetime.datetime(*gameDate, *gameTime)

        #Save Number
        self.fileNum = int(self.filePath.split('\\')[-1][4:])
        self.mySaveNum = intTryParse(self.saveTitle.split()[0])

        if 'AUTOSAVE' in self.saveTitle: #keep the autosaves but we probably won't use them
            self.fileNum = self.fileNum + 10000

def create_table():
    SAVE_DIR_NAME = 'SaveData'
    save_dirs = []
    for item in Path().iterdir():
        if item.is_dir():
            save_dirs.append(Path(item.name + '/' + SAVE_DIR_NAME))
    
    ss = []
    fileNums = set()
    for path in save_dirs:
        for item in path.iterdir():
            if item.is_file() and item.name != 'profile.bin':
                with item.open('r', errors='ignore') as file:
                    obj = Savestate(file)
                    if obj.fileNum not in fileNums:
                        ss.append(obj)
                        fileNums.add(obj.fileNum)
    
    Base.metadata.create_all(engine)
    session = Session()
    session.add_all(ss)
    session.commit()
    
'''
class TitleQueries:
    
    various
    
    ass
    
    rang
    
    snip
    
    tech
    
    gren

    gun
    
    shin
    reaper
    
    psi
    domination
    archon
    
    spec
    hack
'''
def title_query(search_term):
    session = Session()
    result = session.query(Savestate).filter(Savestate.saveTitle.like('%%%s%%' % search_term)).all() 
    return result

LIVE_SAVE_DIRECTORY = 'C:\\Users\\MyDell\\Documents\\My Games\\XCOM2\\XComGame\\SaveData\\'

def send_saves_to_live_dir(result):
    file_paths = [*map(lambda x: Path(x.filePath), result)]
    lsd = Path(LIVE_SAVE_DIRECTORY)
    shutil.rmtree(lsd, ignore_errors=True)
    lsd = Path(LIVE_SAVE_DIRECTORY)
    lsd.mkdir()
    for path in file_paths:
        shutil.copy(path, lsd.joinpath(path.name))





send_saves_to_live_dir(title_query('Before Facility Assault'))






























