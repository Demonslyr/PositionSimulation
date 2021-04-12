from tkinter import *
import tkinter as ttk
from Engine import WclLogParser

'''
    consider using this to find the home directory to store client id/secret
    
    from pathlib import Path
    home = str(Path.home())
'''
log_parser = WclLogParser.WclLogParser()

def grab_log_button_callback():
  report_id = URL_entry.get()
  log_parser.configure(report_id)
  encounter_descriptions = log_parser.encounter_descriptions
  create_encounter_dropdown(encounter_descriptions)

def create_encounter_dropdown(creatureIDs):
  global boss_selected
  dd = []
  for i in range(0, len(creatureIDs)):
    if len(creatureIDs) > 0:
      dd.append(creatureIDs[i]["name"])
  print(dd)
  boss_selected = StringVar(root)
  dropdown = OptionMenu(root, boss_selected, *dd)
  dropdown.pack()
  dropdown.place(x=10, y=50)

  encounterLabel = Label(root, text="Select Encounter to parse")
  encounterLabel.pack()
  encounterLabel.place(x=0, y=30)

  bGO = Button(root, text='Generate SimCraft Movement Script', command=GO)
  bGO.pack()
  bGO.place(x=300, y=50)

  # return boss_selected


def GO():
  boss_selected.get()
  TXY = data_parsing_handler(None)
  out = parse_to_simc_handler(TXY)
  T.delete(1.0, ttk.END)
  for i in out:
    T.insert(ttk.END, str(i) + str('\n'))


OUTPUT_TEXT: str = ''
root = Tk()
root.geometry('650x600')

T = Text(root, height=30, width=80)
T.pack()
T.place(x=2, y=100)
T.insert(ttk.END, OUTPUT_TEXT)

entrylabel=ttk.Label(root, text="WCL Log URL:")
entrylabel.pack()
entrylabel.place(x=0, y=0)
#the entry box
URL_entry = ttk.Entry(root, width=50)
URL_entry.pack()
URL_entry.place(x=80, y=1)

bGRAB = Button(root, text="Grab Log", command=grab_log_button_callback )
bGRAB.pack()
bGRAB.place(x=385)

mainloop()