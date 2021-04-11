from tkinter import *
from tkinter import ttk

OUTPUT_TEXT = ''
root = Tk()
root.geometry('650x600')

T = Text(root, height = 30, width = 80)
T.pack()
T.place(x=2, y=100)
T.insert(ttk.END, OUTPUT_TEXT)

entrylabel=ttk.Label(root, text="WCL Log URL:")
entrylabel.pack()
entrylabel.place(x=0,y=0)
#the entry box
URL_entry = ttk.Entry(root,width=50)
URL_entry.pack()
URL_entry.place(x=80,y=1)

bGRAB = Button(root, text="Grab Log", command=grab_report_code)
bGRAB.pack()
bGRAB.place(x=385)

mainloop()