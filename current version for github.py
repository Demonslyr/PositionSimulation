import http.client
import tkinter as tk 
from tkinter import *
import re
import math


global token
token = {
        'Content-Type': "application/json",
        'Authorization': "Bearer  TOKEN GOES HERE"
}



# hard coding this stuff for now, once I learn dictionaries I feel like this can be cleaned up a lot/be more useful.
# the " suffix on each of the names is because of how the API data gets parsed/stored. 
#currently names is duplicated/used in get_boss_ID. it is actually used in data_parsing_handler
#EIDtable is used in data_parsing_handler
EIDtable=[2398,2418,2383,2402,2405,2406,2412,2399,2417,2407] 
names=['Shriekwing"','Huntsman Altimor"','Hungering Destroyer"','Lady Inerva Darkvein"','Sun King\'s Salvation"',"Artificer Xy\'mox\"",'Council of Blood"','Sludgefist"','Stone Legion Generals"','Sire Denathrius"']


########################################################################################################################################################################
########################################################################################################################################################################

def parse_position(report,start,end,boss_npcID,local_boss_ID):
    #print(report,start,end,boss_npcID,local_boss_ID)
    conn = http.client.HTTPSConnection("www.warcraftlogs.com")
    payload = str("{\"query\":\"{\\n  reportData {\\n    report(code: \\\"")+str(report)+str("\\\") {\\n      events(startTime: ")+str(start)+str(", endTime: ")+str(end)+str(", killType: Kills, hostilityType:Enemies, dataType: DamageTaken, limit: 10000, includeResources: true, targetInstanceID: ")+str(local_boss_ID)+str(" \\n      )\\n        {data nextPageTimestamp}\\n    }\\n  }\\n}\\n\"}")
    headers =token
    conn.request("POST", "/api/v2", payload, headers)
    res = conn.getresponse()
    data = res.read()
    #cleaning the data up a bit
    k=data.decode("utf-8").split("{\"timestamp\":")
    hasNPT=(k[-1].split('"nextPageTimestamp":')) #this is what tells us the new start time for the next query if all the data didn't fit into a single response.
    NPT = hasNPT[-1].strip('}') 
    hasxy=[]
    for i in k:
        if re.search((str("\"targetID\":")+str(boss_npcID)+str(".+\"x\":.+")),i):#NOT ALL OF THE ENTITIES IN OUR LIST HAVE THE X/Y COORDS AT THE SAME INDEX so regex is necessary. 
                hasxy.append(i.split(',')) #if it has an x coordinate, then throw it in our list as a self contained list of all of the returned parameters
    TXY=[]
    for a in hasxy:
        ph=0
        for b in a:
          if (re.search('\"x\":',b)):# janky, but it finds where theres an x coordinate
              TXY.append([a[0],b,a[ph+1]]) #then slaps the corresponding timestamp, the x and the y into TXY
          ph+=1
    #print('len(TXY)',len(TXY))
    return ([NPT,TXY])


#grabs the start time, end time, and encounter ID for the slection
def get_start_end_EID(report,selection):
    conn = http.client.HTTPSConnection("www.warcraftlogs.com")
    payload = str("{\"query\":\"{\\n    reportData {\\n    report(code: \\\"")+str(report)+str("\\\"){fights(killType:Kills){name startTime endTime encounterID}}}}\\n\"}")
    headers = token
    conn.request("POST", "/api/v2", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    s1=data.split('"name":"')
    #print(s1)
    s2=[]
    #cleaning up the data
    for i in range (1,len(s1)):
        s2.append(s1[i].split(','))
        s2[i-1][1]=s2[i-1][1].strip('startTime":')
        s2[i-1][2]=s2[i-1][2].strip('"endTime":')
        s2[i-1][3]=s2[i-1][3].strip('"encounterID":')
        s2[i-1][3]=s2[i-1][3].strip('}')
        s2[i-1][3]=s2[i-1][3].strip(']')
        s2[i-1][3]=s2[i-1][3].strip('}')# I DO NOT KNOW WHY I NEED TO DO THIS TWICE, BUT IF I DONT, IT LEAVES AN EXTRA }
    for i in s2:
        #print(i)
        if selection==i[0]:
            return [i[1],i[2],i[3]] #format is [start,end,encounterID]


def TXY_to_TM(TXY,interval=.2500): #formats the Timestamps and the coordinates into a usable format of [time,total distance moved during that interval]
    #print('in TXY to TM',len(TXY))
    #for i in TXY: print(i)
    Current_interval=[]    
    initial = float(TXY[0][0])
    #initial cleanup and formatting of TXY:
    for i in range (0,len(TXY)):
        #convert time into seconds, and start the counting at 0, rather than at UTC
        TXY[i][0]=round((float(TXY[i][0])-initial)/1000,4)
        wew=''
        lad=''
        #get rid of the "x/y": shit so we can turn the coordinates into ints
        for k in range (4,len(TXY[i][1])):
            wew+=TXY[i][1][k]
            lad+=TXY[i][2][k]
        TXY[i][1]=round(int(wew)/100,2)
        TXY[i][2]=round(int(lad)/100,2)

    TM=[] #holds the time that's elapsed, and how much movement has occurred in the formaat [T,M]. 
    for i in TXY:
        #print(i)
        if len(Current_interval) ==0:
            Current_interval.append(i)
        else:
            if i[0] - Current_interval[0][0] <= interval:
                Current_interval.append(i)
            else:
                Xs=[]
                Ys=[]
                for k in Current_interval:
                    #print(k[1],k[2],Current_interval[0][1],Current_interval[0][2])
                    Xs.append(round(abs(abs(k[1])-abs(Current_interval[0][1])),2))
                    Ys.append(round(abs(abs(k[2])-abs(Current_interval[0][2])),2))
                dxy= round(math.sqrt(max(Xs)**2 + max(Ys)**2),2) #good ole pythagorean theorem. thanks 7th grade math class.
                TM.append([Current_interval[0][0],dxy])
                Current_interval=[]
    #for i in TM: print(i)
    return TM



    #move_threshold:    the minimum distance the move must cover to be inclduded in the results (unit it yards)
    #Twindow:           time between moves before the movement is confirmed as having ended (unit is seconds)
def movement_intervals(TM,move_threshold=3,Twindow=2 ):
    #print('in Move_intervals',len(TM))
    moves=[]
    mStart=0
    mRunTot=0
    mEndFinder=0
    for i in range (0,len(TM)):
        if i==0: #is this the very first iteration of the loop?
            mStart=TM[i][0] 
            mRunTot=TM[i][1]
        else: #if  it's NOT the very first itteration
            if TM[i][1]>0: # was there any movement in this interval?
            #if YES:
                if mRunTot==0:#is it new movement?
                        mStart=TM[i][0]
                        mEndFinder = TM[i][0]
                        mRunTot=TM[i][1]
                else:#or is it a continuation
                        mEndFinder = TM[i][0]
                        mRunTot+=TM[i][1]
            #if no movement this interval:
            else: 
                if TM[i][0]-mEndFinder >= Twindow: #has there been no movement for 3 seconds?
                #IF NO MOVEMENT:
                    if len(moves)==0:#if it's the first move, just slap that shit into moves
                        moves.append([round(mStart,2),mEndFinder,round(mEndFinder-mStart,2),round(mRunTot,2)])
                        mRunTot=0
                    #if it's NOT the first move  
                    elif moves[-1][0] != mStart: #making sure that the line hasn't been added yet (for some reason it likes to add multiples of the same movement if I dont add this check)
                        if mRunTot>=move_threshold: #has the total movement been greater than the threshold? (done to minimize tiny moves that are meaningless)
                            #if yes, then slap it into moves
                            moves.append([round(mStart,2),mEndFinder,round(mEndFinder-mStart,2),round(mRunTot,2)])
                        mRunTot=0   #clear mRunTot because this move is over. regardless of whether or not we saved the move.                
    return(moves)

def get_boss_IDs(report):
    conn = http.client.HTTPSConnection("www.warcraftlogs.com")
    payload = str("{\"query\":\"{\\n    rateLimitData {limitPerHour pointsSpentThisHour pointsResetIn}\\n    reportData {\\n    report(code: \\\"")+str(report)+str("\\\"){ masterData{actors{name id gameID subType} \\n       }}}\\n\\n  \\n   \\n    }\\n    \\n\"}")
    headers = token
    conn.request("POST", "/api/v2", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    #SEEMS LIKE HORRIBLE EFFICIENCY because there's a 3 back to back loops, and lots of splitting things into lists that only get used once,
    #todo: make it suck less
    names=['Shriekwing"','Huntsman Altimor"','Hungering Destroyer"','Lady Inerva Darkvein"','Sun King\'s Salvation"',"Artificer Xy\'mox\"",'Council of Blood"','Sludgefist"','Stone Legion Generals"','Sire Denathrius"']
    boss_npcIDs =    [[],[],[],[],[],[],[],[],[],[]]
    boss_local_IDs = [[],[],[],[],[],[],[],[],[],[]]
    b=data.split(',{"name":"')
    c=[]
    d=[]
    for k in b:
        c.append(k.split(','))
        #print(k)
    for i in c:
        if '"subType":"Boss"}' in i:
            d.append(i)
    for i in range (0,len(d)):
        if d[i][0] in names:
            boss_npcIDs[names.index(d[i][0])].append(d[i][1].strip('"id":'))
            boss_local_IDs[names.index(d[i][0])].append(d[i][2].strip('"gameID":'))
    return [boss_npcIDs,boss_local_IDs]


#THE FUNCTION THAT ORCHASTRATES GETTING THE POSITIONING DATA
#the flow:
#   1) find what boss the user picked, then find the local encounter ID that the report is using for that kill using get_boss_IDs
#   2) find the start and end of that encounter using get_start_end_EID
#   3) generate the TXY list using parse_position. this frequently takes multiple queries so it's done in a while loop 
#
def data_parsing_handler(report):
    global start, end, stuff #making all these variables global feels like it's not what I'm 'supposed to do', but I was lazy and it works.
    #determine the start/end time for that kill
    pick=str(boss_selected.get())+str('"')
    IDs=get_boss_IDs(report)
    boss_npcIDs,boss_local_IDs = IDs[0],IDs[1]
    #print(pick)
    #for i in names: print(i,pick)
    boss_npcID = boss_npcIDs[names.index(pick)][0]
    local_boss_id = boss_local_IDs[names.index(pick)][0]
    #print(boss_npcID,local_boss_id)
    stuff=get_start_end_EID(report,pick)
    #print(stuff)
    start=stuff[0]
    end=stuff[1]
   
    ENCOUNTER_ID = EIDtable[names.index(pick)]
    
    #print('boss_ID:',boss_ID,'ENCOUNTER_ID:',ENCOUNTER_ID, 'start:',start,'end:',end)
   
    #grab all the position data for that boss
    NPT,TXY=parse_position(report,start,end,boss_npcID,local_boss_id)[0],parse_position(report,start,end,boss_npcID,local_boss_id)[1]
    #print(output[0],NPT)
    #print(NPT)
    while NPT != 'null':
        #print('not null')
        #print('start was',start,'\n','NPT is',NPT, 'end =',end)
        ph=parse_position(report,NPT,end,boss_npcID,local_boss_id)
        NPT=ph[0]
        for i in ph[1]:
            TXY.append(i)
    return TXY

    

def drop_down_maker(creatureIDs):
    #print(creatureIDs)
    global boss_selected
    dd=[]
    for i in range (0,len(creatureIDs)):
        if len(creatureIDs[i])>0:
            dd.append(names[i].strip('"'))
    #print(dd)
    boss_selected=StringVar(root)
    dropdown=OptionMenu(root,boss_selected,*dd)
    dropdown.pack()
    dropdown.place(x=10, y=50)
    
    encounterLabel = Label(root, text = "Select Encounter to parse")
    encounterLabel.pack()
    encounterLabel.place(x=0, y=30)
    
    bGO = Button(root,text ='Generate SimCraft Movement Script',command = GO)
    bGO.pack()
    bGO.place(x=300, y = 50)
    
    #return boss_selected


def grab_report_code():
    global report, local_IDs
    url=URL_entry.get()
    kek=url.split('https://www.warcraftlogs.com/reports/')
    topkek=kek[1].split('#')
    report=topkek[0]
    #print(report)
    local_IDs=get_boss_IDs(report)
    drop_down_maker(local_IDs[0])
    
#ONCE YOU CLICK GENERATE SCRIPT:   
def GO(): 
    boss_selected.get()
    TXY=data_parsing_handler(report) #GENERATE TXY
    out=parse_to_simc_handler(TXY) #THEN SEND IT TO GET CLEANED UP AND TURNED INTO A SIMC SCRIPT
    T.delete(1.0,tk.END)
    for i in out:
        T.insert(tk.END, str(i)+str('\n'))

#
# OUTPUTTING STUFF INTO SIMC RAID_EVENTS:
#

#takes the data from TXY, then converts it into a usable format (via TXY_to_TM), then slaps the data into the simcraft format
def parse_to_simc_handler(TXY):
    #I FEEL LIKE THESE LISTS WOULD BE BETTER PLACED OUTSIDE THE FUNCTION, BUT IDK.
    FIGHTS_WITH_ADDS=[2418,2402,2406,2412,2417,2407]# list contains encounterIDs for: HUNTSMAN,INNERVA,SUN KING, COUNCIL, SLG, DENATHRIUS.
    FIGHTS_WITH_DMG_AMPS=[2399]#sludgefist
    FIGHTS_WITH_BOSS_IMMUNES=[2398,2406,2412,2417,2407]#shriekwing, sunking,council,SLG, denathrius
    FIGHTS_WITH_EXTRA_PLAYER_MOVEMENT=[2383,2399] #hungering, sludgefist

    formated_events=[] 
    moves=movement_intervals(TXY_to_TM(TXY))
    if int(stuff[2]) in FIGHTS_WITH_ADDS:
        adds=ADDS(report,start,end)
        for i in adds:
            formated_events.append(i)
    for i in moves:
        formated_events.append(str("raid_events+=/movement,cooldown=9999,distance=")+str(i[3])+str(",duration=")+str(i[2])+str(",first=")+str(i[0]))
    return formated_events


########################################
#  ENCOUNTER SPECIFIC VARIANCES BELOW  #
########################################

def ADDS(report,start,end):
    '''
    if a fight has adds, then we need to detect when those adds spawn, and when they die, as that is the minimum needed to create a raidevent of an add spawn
     right now every add spawn gets it's own raidEvent.
     this is fine for fights with a few adds (huntsman/innerva), but will make fights with lots of adds very messy (easy/obvious example is echos of sin on denathrius p1)
     the first potential solution to this that comes to mind is to collect all the add spawns as we currently do, but to compare the spawn times of the adds in the list, and then group all adds that spawn within a certain time window
     the obvious way of determining the duration of a group of adds is to calculate the average (mean or median) lifespan of the adds in that grouping. if we want to be fancy, simcraft has functionality for creating a distribution of durations given a mean and standard deviation
     One solvable complicating factor in doing this is when multiple adds spawn that have significantly different HPs, such that they die at very different times. the most obvious example of this is innerva, so some extra consideration should be made
    
    SMALL BUG: killing critters (such as killing a bug, ironically) shows their death in the logs, and therefore creates a raidevent of spawning an add with duration=0.0, which is dumb and pointless.
    EXAMPLE: https://www.warcraftlogs.com/reports/K1Y6fhxajZCq3mF9#fight=7&type=deaths&hostility=1
      on huntsman a dusty widow dies to a fell rush @2:59, which creates the raidevent: raid_events+=/adds,count=1,first=179.58,duration=0.0,cooldown=9999
    *should add functionality to ignore any spawns whos duration is under a certain threshold to remove this clutter.
    '''
    conn = http.client.HTTPSConnection("www.warcraftlogs.com")
    payload = str("{\"query\":\"{reportData {\\n    report(code: \\\"")+str(report)+str("\\\"){  table(startTime:")+str(start)+str(", endTime: ")+str(end)+str(",hostilityType:Enemies dataType:Deaths) }\\n\\n  \\n   \\n    }}\\n    \\n\"}")
    headers = token
    conn.request("POST", "/api/v2", payload, headers)
    resp = conn.getresponse()
    data = resp.read().decode("utf-8").split('}]},{') #the magic string that splits the adds up nicely
    data[0]=data[0].split('{"data":{"reportData":{"report":{"table":{"data":{"entries":[{')[1]#this is just to make the first index consistent with the rest of the splits

    SPLIT_DATA=[]
    for i in range (0, len(data)): 
        ph=data[i].split(',')
        SPLIT_DATA.append(ph)
    deathWindow=[]
    timestamps=[]
    #there's probably a less convoluted way of doing this
    for i in SPLIT_DATA:
        #find the full strings that contain the substrings that I am looking for
        dw = [p for p in i if '"deathWindow":' in p] 
        ts= [q for q in i if '"timestamp":' in q]
        #then grab the actual indexes of those full strings
        ph=i.index(dw[0])
        ph2=i.index(ts[0])
        #print(i[ph])
        #once we have found the elements we are interested in, append them to their corresponding lists.
        deathWindow.append(i[ph])
        timestamps.append(i[ph2])
    death_times=[]
    life_duration=[]
    for i in range (0,len(SPLIT_DATA)-1):#-1 because the table includes the bosses death, which  this function doesnt care about
        death_times.append(int(timestamps[i].strip('"timestamp":')))#timestamp is the time of death.
        life_duration.append(int(deathWindow[i].strip('"deathWindow":')))#deathWindow is how long it was alive

    Adds=[] #format [spawn time,duration] for each add.
    for i in range(0,len(death_times)):
        #therefore we can determine spawn time =  death Timestamp - deathwindow, then i subtract the start time of the encounter to time times make sense.
        spawn=round((death_times[i]-life_duration[i]-int(start))/1000,2)
        Adds.append([spawn,round(life_duration[i]/1000,2)])
    adds_events=[]
    for i in Adds:
        adds_events.append(str("raid_events+=/adds,count=1,first=")+str(i[0])+str(",duration=")+str(i[1])+str(",cooldown=9999"))
        #print("raid_events+=/adds,count=1,first=",i[0],"duration=",i[1])
    return adds_events


#when immune phases are detected, this function pulls that information from the report 
#https://www.wowhead.com/spell=328921/blood-shroud this is the one that causes the immunity.

#MINIMUM INFORMATION NEEDED TO GENERATE Raid_event:
#   1) start time
#   2) Duration
#   3) do we pick a new target when the invulnerability happens?
def IMMUNE_PHASES():
    pass



#for hungering/sludgefist, ALL players runs away from the boss while the boss remains stationary, so default method of tracking boss movement is not sufficient.
#YES WE COULD IMPLEMENT THE RANDOM RUN OUT MECHANICS AND STUFF. NO I DON'T WANT TO.
#while that technically makes the simulation 'more accurate' doing so just adds more variance/randomness that conflicts with what the entire point of this project is meant to accomplish 
# that is:
#   1)  trying to generate an accurate approximation of what your gear is capable of on a given fight. This is meant to be the upperbound, as it simulates perfect play. It makes no sense to me to inject variances that will make generating that upper bound less accurate
#   2)  optimizing gear decisions on a per fight basis. my gut feeling is that random runout mechanics are extremly unlikely to have any meaningful impact on gearing decisions. 
#that said, if we ever get bored enough to implement random run out mechanics, then I would expect there to be a toggle to turn them on and off. 
def EXTRA_PLAYER_MOVENTS():
    pass


#sludgefist takes increased damage every time he smashes a pillar. currently this is the only fight like this, but this should be future proofed for upcoming content
#MINIMUM INFORMATION NEEDED TO GENERATE RAID_EVENT:
#   1) start time
#   2) Duration
#   3) damage multiplier
def DMG_AMP():
    pass



#this is a variance designed to handle creating overrides for encounters that give you special buffs
#e.g.: the haste buff granted by the dance phase on council
def CUSTOM_BUFFS():
    pass


'''
THINKING OUT LOUD:

SLG:
    a seemingly straight forward way to simulate the bosses is to treat is as 1 boss with immune phases + an add that spawns for p3 that's treated as the 2nd boss.
    the  obvious problem with this is that it will not accurately simulate condemns >80% usability.
    it's possible to set particular unit's initial HP% (this is what raidbots does for execute patchwork sims)
        enemy="NAME"
        enemy_initial_health_percentage="20"
    it's not immediately clear how to use this in conjuction with creating the "boss" add for p3. but I see no obvious reasons why there wouldn't be a way to do it.

    assuming that that works out, we gotta deal with the fact that after each intermission, you get a new boss, and therefore it effectively "heals" back to full HP.
    There might be a way to implement a raid_event to heal the boss during the immunity phases
    


'''




#########################################################################################################################################################
#########################################################################################################################################################
#SPAWNING THE GUI, AND GETTING EVERYTHING INITIALIZED HAPPENS BELOW
#########################################################################################################################################################
#########################################################################################################################################################
#########################################################################################################################################################
    
OUTPUT_TEXT = ''
root = Tk()
root.geometry('650x600')


T = Text(root, height = 30, width = 80) 
T.pack()
T.place(x=2, y=100)
T.insert(tk.END, OUTPUT_TEXT)

entrylabel=tk.Label(root, text="WCL Log URL:")
entrylabel.pack()
entrylabel.place(x=0,y=0)
#the entry box
URL_entry = tk.Entry(root,width=50)
URL_entry.pack()
URL_entry.place(x=80,y=1)

bGRAB = Button(root, text="Grab Log", command=grab_report_code)
bGRAB.pack()
bGRAB.place(x=385)






mainloop()
