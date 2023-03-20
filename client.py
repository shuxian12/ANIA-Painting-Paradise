# import tkinter as tk
from tkinter import *
from tkinter import colorchooser, messagebox, ttk
from PIL import ImageTk, Image
import random
import socket
import threading
import pickle
# import json


class GUI:

    def __init__(self, master):
        self.username = 'user'
        self.root = master
        self.client_socket = None
        self.first = 0
        self.mission = 0
        self.shapeFirst = 0

        self.fill = 0

        self.lr_preX, self.lr_preY, self.r_preX, self.r_preY = None, None, None, None
        self.startX, self.startY, self.preX, self.preY = None, None, None, None

        self.canvas = None

        self.colorBtn = None
        self.color = "#" + \
            ''.join([random.choice('0123456789ABCDEF') for _ in range(6)])
        self.r_color = ''

        self.brushSizeScale = None
        self.brushSize, self.r_brushSize = 1, 1
        self.brushLabel = None

        self.image = Image.open('test1.jpg')
        self.image = self.image.resize((225, 150), Image.ANTIALIAS)
        self.image2 = Image.open('enniya.jpg')
        self.image2 = self.image2.resize((215, 120), Image.ANTIALIAS)
        self.img_ref = []

        self.paintSelect = None
        self.paintWay, self.r_paintWay = None, None
        self.init_socket()
        self.init_gui()
        self.create_name_top_level()
        self.listen_for_incoming_messages_in_a_thread()

    def init_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_ip = '127.0.0.1'
        remote_port = 48763
        self.client_socket.connect((remote_ip, remote_port))

    def init_gui(self):
        self.root.title("ANIA's Painting Paradise")
        self.root.resizable(0, 0)
        self.display_whiteboard()

    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(
            target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def create_name_top_level(self):
        self.top = Toplevel(self.root)
        self.top.title('Please enter your name!!')
        self.top.geometry('300x100+350+300')
        name_topic = Label(self.top, text='Please enter your name:')
        name_topic.pack()
        self.name_entry = Entry(self.top, width=20)
        self.name_entry.pack(padx=10, pady=10)
        self.enter_name = Button(self.top, text='Enter', command=self.enter_name, padx=10, pady=10)
        self.enter_name.pack()

    def enter_name(self):
        self.username = self.name_entry.get()
        self.top.destroy()

    def receive_message_from_server(self, so):
        while 1:
            buffer = so.recv(512)
            if not buffer:
                break

            details = pickle.loads(buffer)
            # print(details)
            if details.get('mission') == 1:
                msg = details.get('message')
                self.text_message.insert('end', str(details.get('username')) + ': ' + msg)
            else:
                self.r_paintWay = details.get('way')
                # print(self.r_paintWay)
                self.r_color = details.get('color')
                self.r_brushSize = details.get('size')
                if details.get('fill') == 1:
                    self.filledup_receive()
                    continue
                if (self.r_paintWay == 'pen' or self.r_paintWay == 'block' or self.r_paintWay == 'dot' or self.r_paintWay == 'eraser'):
                    if details.get('first'):
                        self.lr_preX = details.get('preX')
                        self.lr_preY = details.get('preY')
                    else:
                        self.r_preX = details.get('preX')
                        self.r_preY = details.get('preY')
                        self.draw_receive()

                if self.r_paintWay == 'maomao' or self.r_paintWay == 'enniya':
                    self.put_image_receive(details.get('startX'), details.get('startY'),self.r_paintWay)
        so.close()

    def display_whiteboard(self):
        self.root.geometry('960x630')   # '487x630'
        self.display_brushes_attribute()
        self.create_chat_room()
        self.display_canvas_area()

    def create_chat_room(self):
    #     print('create chat room')
        message_frame = Frame(self.root, width=400, height=560, padx=5, pady=5, bg='#FFFFF0')
        self.text_message = Text(message_frame,width=50)
        self.text_text = Text(message_frame,width=50, height=15, pady=10)
        self.send_button = Button(message_frame, text='send',activeforeground='#f00', pady=5, command=self.chatting)   # , command=lambda: self.send_message(text_text)
        self.text_message.pack()
        self.text_text.pack()
        self.send_button.pack(side=LEFT)
        message_frame.pack(side='right')    #, fill='both'

    def chatting(self):
        # print('chatting')
        send_msg = self.text_text.get('0.0', 'end')
        self.text_message.insert('end', "me: "+send_msg)
        self.text_text.delete('0.0', 'end')
        # self.text_message.see('end.end')
        self.mission = 1
        if '貓貓' in send_msg:
            newWindow = Toplevel(self.root)
            newWindow.title('貓貓')
            newWindow.geometry('500x500')
            image = Image.open('luckymaomao.jpeg')
            image = image.resize((500, 500), Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(image)
            label = Label(newWindow, image=self.photo, width=500, height=500)  # 在 Lable 中放入圖片
            label.pack()
            return
        self.send_message(send_msg)

    def display_brushes_attribute(self):
        frame = Frame(self.root, padx=5, pady=5, bg='white')
        self.colorBtn = Button(frame, bg=self.color, padx=40, bd=1,
                               command=self.colorPick)
        self.colorBtn.grid(row=0, column=0, padx=5)
        self.filledupBtn = Button(frame, text="filled up", font=("Cambria", 10), bd=1,
                             command=self.filledup)
        self.filledupBtn.grid(row=0, column=1, padx=5)
        self.brushSizeScale = Scale(
            frame, from_=1, to=30, bg='white', showvalue=False, bd=0, orient=HORIZONTAL, command=self.get_brushSize)
        self.brushSizeScale.grid(row=0, column=2, padx=5)
        self.brushLabel = Label(
            frame, bg='white', text='size: '+str(self.brushSize))
        self.brushLabel.grid(row=0, column=3, padx=5)
        self.paintSelect = ttk.Combobox(
            frame, values=['pen', 'block', 'dot', 'eraser','-------------', 'enniya', 'maomao'], width=15)
        self.paintSelect.grid(row=0, column=4, padx=5)
        self.paintSelect.current(0)
        frame.pack(fill='x')

        
    def colorPick(self):
        self.color = colorchooser.askcolor()[1]
        # print(self.color)
        self.colorBtn.configure(bg=self.color)  # macos 不支援

    def filledup(self):
        self.mission = 0
        self.fill = 1
        self.canvas.delete('all')
        self.canvas.configure(bg=self.color)
        self.send_detail()
        self.fill = 0
        self.img_ref.clear()

    def filledup_receive(self):
        self.canvas.delete('all')
        self.canvas.configure(bg=self.r_color)
        self.img_ref.clear()

    def get_brushSize(self, val):
        self.brushSize = val
        self.brushLabel['text'] = 'size: ' + str(val)
        # print(val)

    def display_canvas_area(self):
        self.canvas = Canvas(self.root, bg='black')
        self.canvas.pack(
            anchor='nw', fill='both', expand=1)
        self.canvas.bind("<Button-1>", self.get_X_and_Y)    #滑鼠左鍵點擊
        self.canvas.bind("<B1-Motion>", self.draw)          #滑鼠左鍵拖曳

    def draw(self, event):
        self.mission = 0
        self.first = 0
        if self.paintWay == 'pen':
            self.canvas.create_line(
                (self.preX, self.preY, event.x, event.y), width=self.brushSize, fill=self.color, capstyle=ROUND)
        elif self.paintWay == 'block':
            self.canvas.create_rectangle(
                (self.preX, self.preY, event.x, event.y), fill=self.color)
        elif self.paintWay == 'dot':
            self.canvas.create_oval(
                (self.preX, self.preY, event.x, event.y), fill=self.color)
        elif self.paintWay == 'eraser':
            self.canvas.create_line(
                (self.preX, self.preY, event.x, event.y), width=self.brushSize, fill='black', capstyle=ROUND)
        self.preX, self.preY = event.x, event.y
        self.send_detail()

    def draw_receive(self):
        if self.r_paintWay == 'pen':
            self.canvas.create_line(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), width=self.r_brushSize, fill=self.r_color, capstyle=ROUND)
        elif self.r_paintWay == 'block':
            self.canvas.create_rectangle(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), fill=self.r_color)
        elif self.r_paintWay == 'dot':
            self.canvas.create_oval(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), fill=self.r_color)
        elif self.r_paintWay == 'eraser':
            self.canvas.create_line(
                (self.lr_preX, self.lr_preY, self.r_preX, self.r_preY), width=self.r_brushSize, fill='black', capstyle=ROUND)
        self.lr_preX, self.lr_preY = self.r_preX, self.r_preY

    def get_X_and_Y(self, event):
        self.mission = 0
        self.first = 1
        self.shapeFirst = 1
        self.paintWay = self.paintSelect.get()
        self.preX, self.preY = event.x, event.y
        self.startX, self.startY = event.x, event.y
        if self.paintWay == 'maomao' or self.paintWay == 'enniya':
            self.put_image(self.paintWay)
        self.send_detail()
    
    def put_image(self, event=None):
        if event == 'maomao':
            self.photo = ImageTk.PhotoImage(self.image)
        else:
            self.photo = ImageTk.PhotoImage(self.image2)
        self.canvas.create_image(self.startX, self.startY, image=self.photo)    # , anchor='center'
        self.img_ref.append(self.photo)

    def put_image_receive(self, x, y, event):
        if event == 'maomao':
            self.photo = ImageTk.PhotoImage(self.image)
        else:
            self.photo = ImageTk.PhotoImage(self.image2)
        self.canvas.create_image(x, y, image=self.photo)
        self.img_ref.append(self.photo)

    def send_message(self, msg):
        self.mission = 1
        details = pickle.dumps(
            {"mission": self.mission, "message": msg, "username": self.username})
        # self.client_socket.send(details.encode('utf-8'))
        self.client_socket.send(details)

    def send_detail(self):
        details = pickle.dumps(
            {"mission": self.mission,"first": self.first, "shapeFirst": self.shapeFirst, "fill": self.fill, "color": self.color, "size": self.brushSize, "way": self.paintWay, "preX": self.preX, "preY": self.preY, "startX": self.startX, "startY": self.startY})
        self.client_socket.send(details)

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.send(pickle.dumps('close'))
            self.client_socket.close()
            exit(0)


if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()