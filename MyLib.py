from msilib.schema import File
import os
from datetime import datetime
import shutil
import pandas as pd



logfailedls = 'logfailed.txt'
logsuccessls = 'logsuccess.txt'



def CenterWiseFolderCreate(MainFolder,CenterType):
    FullPath = MainFolder+'/'+CenterType
    if not os.path.exists(FullPath):
        os.makedirs(FullPath)
    


def logwriter(ctype,ip,locName,status):
       if status == True:
        logsuccess = open('{}/{}'.format(ctype,logsuccessls),'a')
        logsuccess.write('{}  : {}-{}\n'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),ip,locName))
        logsuccess.close()
       elif status == False:
        logfailed = open("{}/{}".format(ctype,logfailedls),'a')
        logfailed.write('{}  : {}-{}\n'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),ip,locName))
        logfailed.close()




#conatanating dataframe list and stacking verticaly
def dfConcat(dflist):
    concatedDf = pd.DataFrame()
    for i in dflist:
        concatedDf = pd.concat([concatedDf,i],axis=0,ignore_index=True)
    return concatedDf



#save the current query to text file
def QueryToFilesaver(Filename,query):
    queryFile = open('{}/query.txt'.format(Filename),'a')
    queryFile.write(query)
    queryFile.close()

    

#create folder
def FolderCreate(Filename):
    if os.path.exists(Filename):
        shutil.rmtree(Filename)
    os.makedirs(Filename)

    



def locdetailswrite(Filename,loclist):
    indexid = 1
    if (len(loclist) != 0):
        locationsfile = open('{}/failed.txt'.format(Filename),'w')
        for key,info in loclist.items():
            for key,value in info.items():
                locationsfile.write('{}). [{}] [{}]\n'.format(indexid,key,value))
                indexid += 1
        locationsfile.close()
        
        
def AllLocsIPToList(locationDict,CenterChoices):
    IpList = []
    for CenterType,CenterDictInfo in locationDict.items():
        for ip,LocationName in CenterDictInfo.items():
            if CenterType in CenterChoices:
                IpList.append(ip)
            
    return IpList


def ReturnCenter_Type_Name(ip,locations):
    for key,values in locations.items():
        if ip in values:
            return key,values[ip]
        

def listappend(lists):
    mainlist = []
    for index in lists:
        for listitme in index:
            mainlist.append(listitme)
            
    return mainlist
        


def loclistwrite(filename,iplist):
   
    locationsfile = open('{}/failediplist.txt'.format(filename),'w')
    for i in iplist:
         locationsfile.write('{}\n'.format(i))