from tkinter import *
from tkinter import tk
from WclLogParser import *
'''
    consider using this to find the home directory to store client id/secret
    
    from pathlib import Path
    home = str(Path.home())
'''
log_parser = WclLogParser()


def create_bossDropdown(creatureIDs):
  global boss_selected
  dd = []
  for i in range(0, len(creatureIDs)):
    if len(creatureIDs[i]) > 0:
      dd.append(names[i].strip('"'))
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
  TXY = data_parsing_handler(report)
  out = parse_to_simc_handler(TXY)
  T.delete(1.0, tk.END)
  for i in out:
    T.insert(tk.END, str(i) + str('\n'))

OUTPUT_TEXT = ''
root = Tk()
root.geometry('650x600')

T = Text(root, height = 30, width = 80)
T.pack()
T.place(x=2, y=100)
T.insert(tk.END, OUTPUT_TEXT)

entrylabel=ttk.Label(root, text="WCL Log URL:")
entrylabel.pack()
entrylabel.place(x=0,y=0)
#the entry box
URL_entry = tk.Entry(root,width=50)
URL_entry.pack()
URL_entry.place(x=80,y=1)

bGRAB = Button(root, text="Grab Log", command= lambda: log_parser.configure(URL_entry.get()))
bGRAB.pack()
bGRAB.place(x=385)

mainloop()