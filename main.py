__author__ = 'grupo_k-tegshig_tim'

import tkinter as tk
from tkinter import ttk
#from sense_emu import SenseHat
from tkinter.messagebox import showinfo
import time
import datetime
import json
import paho.mqtt.client as mqtt

class Aplicacion1:
    def __init__(self):
        def on_connect(client, userdata, flags, rc):
            print("Connectedd with result code"+str(rc))
            client.subscribe("grupo_k/data")
        def on_message(client, userdata, msg):
            if(self.continue_recording):
                data = json.loads(msg.payload)
                self.distance=(data["distance"])
                self.temp=(data["temp"])
                self.light=(data["light"])
                self.var1.set("Distance: "+str(int(self.distance)))
                self.var2.set("Temperature: "+str(int(self.temp)))
                self.var3.set("Light: "+str(int(self.light)))
                self.record()

        self.client=mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect("broker.mqttdashboard.com", 1883, 60)
        self.client.loop_start()

        self.ventana1=tk.Tk()
        menubar1 = tk.Menu(self.ventana1)
        self.ventana1.config(menu=menubar1)
        self.counter = 1
        self.continue_recording= False

        self.sum_light=0
        self.sum_temp=0

        self.var1 = tk.StringVar()
        self.var1.set("Distance: ")
        self.var2 = tk.StringVar()
        self.var2.set("Temperature: ")
        self.var3 = tk.StringVar()
        self.var3.set("Light: ")
        self.var4 = tk.StringVar()
        self.var4.set("Distance Threshold: 20")
        self.var5 = tk.StringVar()
        self.var5.set("Status: ")

        self.ave1 = tk.StringVar()
        self.ave1.set("Average Temperature:")
        self.ave2 = tk.StringVar()
        self.ave2.set("Average Light: ")

        self.threshold = tk.IntVar()
        self.threshold = 20

        self.ventana1.title("Sprinkler Project")
        self.cuaderno1 = ttk.Notebook(self.ventana1)

        self.pagina0 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina0, text="Control")

        self.labelframe1=ttk.LabelFrame(self.pagina0, text="Sensors Control:")
        self.labelframe1.grid(column=0, row=0, sticky="WE")
        self.control()

        self.labelframe2=ttk.LabelFrame(self.pagina0, text="Current values:")
        self.labelframe2.grid(column=1, row=0, sticky="WE")
        self.currentvalues()

        self.labelframe11=ttk.LabelFrame(self.pagina0, text="Automatic Stop:")
        self.labelframe11.grid(column=2, row=0, sticky="WE")
        self.automaticpause()

        self.pagina1 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina1, text="Value")

        self.labelframe3=ttk.LabelFrame(self.pagina1, text="Historico")
        self.labelframe3.grid(column=0, row=2, sticky="news")
        self.historico()

        self.pagina2 = ttk.Frame(self.cuaderno1)
        self.cuaderno1.add(self.pagina2, text="Summary")

        self.label2=ttk.Label(self.pagina2, text="Grafica aqui")
        self.label2.grid(column=0, row=0)
        self.labelframe1=ttk.LabelFrame(self.pagina2, text="Calculate:")
        self.labelframe1.grid(column=0, row=0, sticky="WE")
        self.summary()

        #self.labelframe51=ttk.LabelFrame(self.pagina0, text="Sprinklers Status:")
        #self.labelframe51.grid(column=3, row=0, sticky="WE")
        #self.sprinkler()

        self.cuaderno1.grid(column=0, row=0)
        self.ventana1.mainloop()
    
    def sprinkler(self):
        self.label1 = ttk.Label(self.labelframe51, textvariable="text") 
        self.label1.grid(column=0, row=1)
        
    def currentvalues(self):
        self.label1 = ttk.Label(self.labelframe2, textvariable=self.var1) 
        self.label1.grid(column=0, row=1)
        self.label1 = ttk.Label(self.labelframe2, textvariable=self.var2) 
        self.label1.grid(column=0, row=2)
        self.label1 = ttk.Label(self.labelframe2, textvariable=self.var3) 
        self.label1.grid(column=0, row=3)

    def automaticpause(self):
        self.label1 = ttk.Label(self.labelframe11, textvariable=self.var4) 
        self.label1.grid(column=0, row=0)
        self.uname = tk.StringVar()
        self.entry = tk.Entry(self.labelframe11, textvariable = self.uname)
        self.entry.grid(column=0, row=1, columnspan=3)
        self.Nb = ttk.Button(self.labelframe11, text = 'Confirm', command = self.newthreshold)
        self.Nb.grid(column=0, row=2, columnspan=3)
        self.label1 = ttk.Label(self.labelframe11, textvariable=self.var5) 
        self.label1.grid(column=0, row=3)

    def newthreshold(self):
        self.threshold=int(self.entry.get())
        print(self.threshold)
        self.var4.set("Distance Threshold: "+str(int(self.entry.get())))

    def historico(self):
        self.scroll1 = tk.Scrollbar(self.labelframe3, orient=tk.VERTICAL)
        self.tree = ttk.Treeview(self.labelframe3, yscrollcommand=self.scroll1.set)
        self.tree.grid(column=0, row=0, columnspan=3)

        self.scroll1.configure(command=self.tree.yview)
        self.scroll1.grid(column=4, row=0, sticky='NS')    # NS de norte a sur

        # https://tkdocs.com/tutorial/tree.html
        self.tree['columns'] = ('one', 'two', 'three', 'modified')

        # self.tree.column('one', 'two', 'three', width=100, anchor='center')
        self.tree.heading('#0', text='#Num')
        self.tree.heading('one', text='Distance')
        self.tree.heading('two', text='Temperature')
        self.tree.heading('three', text='Light')
        self.tree.heading('modified', text='Date')

    def control(self):
        ttk.Style().configure("DG.TButton", background="darkgreen")
        ttk.Style().configure("DR.TButton", background="darkred")
        self.boton=ttk.Button(self.labelframe1, text="Start", command=self.start_recording, style="DG.TButton")
        self.boton.grid(column=0, row=0)
        self.boton2=ttk.Button(self.labelframe1, text="Stop", command=self.stop_recording, style="DR.TButton")
        self.boton2.grid(column=1, row=0)

    def summary(self):
        self.boton1=ttk.Button(self.labelframe1, text="Summarize", command=self.summarize)
        self.boton1.grid(column=0, row=0, sticky="WE")
        self.label1 = ttk.Label(self.labelframe1, textvariable=self.ave1) 
        self.label1.grid(column=0, row=1)
        self.label1 = ttk.Label(self.labelframe1, textvariable=self.ave2) 
        self.label1.grid(column=0, row=2) 

    def summarize(self):
        showinfo("Summary", "Calculating Average")
        self.ave1.set("Average Temperature: "+str(int(self.sum_temp/self.counter)))
        self.ave2.set("Average Light: "+str(int(self.sum_light/self.counter)))        

    def start_recording(self):
        self.continue_recording = True

    def stop_recording(self):
        self.continue_recording = False

    def temp_button(self):
        showinfo("Place", "Holder")

    def record(self):
        localtime = time.asctime( time.localtime(time.time()) )
        distance = self.distance
        temp = self.temp
        light = self.light
        if((self.threshold)>(self.distance)):
            self.var5.set("Status: Under Threshold")
        else:
            self.var5.set("Status: Over Threshold")
        self.tree.insert('', 'end', text=str(self.counter), values=(distance, temp, light, time.asctime( time.localtime(time.time()) )))
        self.sum_light+=int(light)
        self.sum_temp+=int(temp)
        self.counter+=1

aplicacion1=Aplicacion1()
