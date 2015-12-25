import zmq, sys, threading, json
from Tkinter import *
import tkMessageBox

###################################################################
#  Backend(output, writeHandler, ip, port)                        #
#                                                                 #
#  Thread para receber as mensagens e escreve-las no sitio certo  #
#                                                                 #
###################################################################

class Backend(threading.Thread):
    def __init__(self, output, writeHandler, ip, port):
        super(Backend, self).__init__ ()
        self._stop = threading.Event() #not sure if we need this
        self.output = output           #ponteiro do sitio onde se escreve
        self.writeHandler = writeHandler #funcao para escrever
        self.port = port  #porto de subscribe
        self.ip = ip

    #recebe e escreve no sitio certo
    def run(self):
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://' + self.ip + ':'+str(self.port))
        sub.setsockopt(zmq.SUBSCRIBE, "")
        while True:
            message = sub.recv() #recebe
            message = json.loads(message)
            message = message["user"] + ": " + message["text"] #edita
            self.writeHandler(self.output, message) #escreve

###################################################################
#  Frontend(ip, port)                                             #
#                                                                 #
#   Simplesmente envia as cenas para o porto de pull do servidor  #
#                                                                 #
###################################################################

class Frontend():
    def __init__(self, ip, port):
        self.input = input
        ctx = zmq.Context()
        self.output = ctx.socket(zmq.PUSH) #porto de push
        self.output.connect('tcp://' + ip + ':' + str(port))
        #ainda nao ta protegido contra falhas

    def send(self, msg):
        self.output.send_string(msg) #envia a mensagem

    def stop(self): #not sure if we need this
        self.output.close()

###################################################################
#  ChatClient(root)                                               #
#                                                                 #
#   Interface grafica para o utilizador, com espaço para definir  #
#   os enderecos do servidor e escolher o seu username, um espaco #
#   para escrever as mensagens, butoes para efectuar as accoes e  #
#   um ecra para ler as mensagens recebidas                       #
#                                                                 #
###################################################################

class ChatClient(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.root = root
        self.input_port_set = False
        self.output_port_set = False
        self.username = ""
        self._initInterface()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        #associa o handler de enceramento

    def _initInterface(self):
        self.root.title("Chat") #titulo

        self.root.resizable(width=False, height=False)

        paddedMain = Frame(self.root)     #frame principal, com margens
        paddedMain.grid(padx=5, pady=5, stick=E+W+N+S) #posiciona a frame

        settingsGrid = Frame(paddedMain) #frame para a barra dos settings
        settingsGrid.grid(sticky=E+W+N)

        nameGrid = Frame(settingsGrid)
        nameGrid.grid(row=0, column=0, sticky=E+N)

        self.nameVar = StringVar()
        nameLabel = Label(nameGrid, text = "Username")
        nameLabel.grid(row=0, sticky= W+N+S)
        self.nameField  = Entry(nameGrid, width=23, textvariable=self.nameVar)
        self.nameField.grid(row=1, sticky=N+S)
        self.nameField.bind("<Return>", self.handleSetName)
        self.nameButton = Button(nameGrid, text="Set", width=3, command=self.handleSetName)
        self.nameButton.grid(row=1, sticky=E+N+S)

        serverGrid = Frame(settingsGrid)
        serverGrid.grid(row=0, column= 1, sticky=N)

        self.serverVar = StringVar()
        self.serverVar.set("9000")
        serverLabel = Label(serverGrid, text = "Server Port")
        serverLabel.grid(row=0, sticky= W+N+S)
        self.serverField  = Entry(serverGrid, width=23, textvariable=self.serverVar)
        self.serverField.grid(row=1, sticky = N+S)
        self.serverField.bind("<Return>", self.handleSetServer)
        self.serverButton = Button(serverGrid, text="Set", width=3, command=self.handleSetServer)
        self.serverButton.grid(row=1, sticky = E+N+S)

        clientGrid = Frame(settingsGrid)
        clientGrid.grid(row=0, column=2, sticky=E+N)

        self.clientVar = StringVar()
        self.clientVar.set("8000")
        clientLabel = Label(clientGrid, text = "Client Port")
        clientLabel.grid(row=0, sticky= W+N+S)
        self.clientField  = Entry(clientGrid, width=23, textvariable=self.clientVar)
        self.clientField.grid(row=1, sticky = N+S)
        self.clientField.bind("<Return>", self.handleSetClient)
        self.clientButton = Button(clientGrid, text="Set", width=3, command=self.handleSetClient)
        self.clientButton.grid(row=1, sticky = E+N+S)

        recievedGrid = Frame(paddedMain)
        recievedGrid.grid(padx=0)

        self.RMessages = Text(recievedGrid, bg="white", state=DISABLED)
        self.RMessages.pack()

        sendingGrid = Frame(paddedMain)
        sendingGrid.grid()

        self.SMessageText = StringVar()
        self.SMessageField = Entry(sendingGrid, width=63, textvariable=self.SMessageText)
        self.SMessageField.grid(row=0, column=0, sticky=W)
        self.SMessageField.bind("<Return>", self.handleSend)

        sendButton = Button(sendingGrid, text="Send", command=self.handleSend)
        sendButton.grid(row=0, column=1, sticky=E)

    #arranca o servidor de subscribe
    def _initServer(self, ip, port):
        self.backend = Backend(self.RMessages, self.handleRecieve, ip, port)
        self.backend.start()

    #handler para receber mensagens
    def handleRecieve(self, output, msg):
        output.config(state=NORMAL)
        output.insert("end", msg+"\n")
        output.config(state=DISABLED)

    #handler para enviar mensagens
    def handleSend(self, event=None):
        if self.username != "" and self.output_port_set and self.input_port_set:
            message = self.SMessageText.get()
            self.SMessageText.set("")
            message = {
                "text": message,
                "user": self.username
            }
            self.frontend.send(json.dumps(message))
        else:
            if self.username == "":
                tkMessageBox.showwarning("Error!", "Please set your username first!")
            elif not self.output_port_set:
                tkMessageBox.showwarning("Error!", "Please set the server port first!")
            elif not self.input_port_set:
                tkMessageBox.showwarning("Error!", "Please set the client port first!")

    #handler para estabelecer o nome
    def handleSetName(self, event=None):
        name = self.nameVar.get()
        if name != "":
            self.username = name
            self.nameField.config(state=DISABLED) #so se pode escolher o nome uma vez
            self.nameButton.config(state=DISABLED)
        else:
            tkMessageBox.showwarning("Error", "Invalid Username!")

    def handleSetServer(self, event=None):
        try:
            self.input_port = int(self.serverVar.get())
            self.input_port_set = True
            self.serverField.config(state=DISABLED)
            self.serverButton.config(state=DISABLED)
            self._initServer("localhost", self.input_port)
        except:
            tkMessageBox.showwarning("Error", "Invalid port number!")

    def handleSetClient(self, event=None):
        try:
            self.output_port = int(self.clientVar.get())
            self.output_port_set = True
            self.clientField.config(state=DISABLED)
            self.clientButton.config(state=DISABLED)
            self.frontend = Frontend("localhost", self.output_port)
        except:
            tkMessageBox.showwarning("Error", "Invalid port number!")

    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            if self.input_port_set:
                self.backend._Thread__stop()
            if self.output_port_set:
                self.frontend.stop()
            self.root.destroy()

def main():
    root = Tk()
    app = ChatClient(root)
    root.mainloop()

if __name__ == '__main__':
  main()
