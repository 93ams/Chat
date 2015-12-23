import zmq, sys, threading
from Tkinter import *

class Backend(threading.Thread):
    def __init__(self, output, writeHandler, port):
        threading.Thread.__init__ (self)
        self._stop = threading.Event()
        self.output = output
        self.writeHandler = writeHandler
        self.port = port

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        ctx = zmq.Context()
        sub = ctx.socket(zmq.SUB)
        sub.connect('tcp://localhost:'+str(self.port))
        sub.setsockopt(zmq.SUBSCRIBE, "")
        while not self.stopped():
            message = sub.recv()
            self.writeHandler(self.output, message)
        sub.close()

class Frontend():
    def __init__(self, port):
        self.input = input
        ctx = zmq.Context()
        self.output = ctx.socket(zmq.PUSH)
        self.output.connect('tcp://localhost:'+str(port))

    def send(self, msg):
        self.output.send(msg)

class ChatClient(Frame):
    def __init__(self, root, input_port, output_port):
        Frame.__init__(self, root)
        self.root = root
        self._initInterface()
        self._initServer(input_port)
        self.frontend = Frontend(output_port)

    def _initInterface(self):
        self.root.title("Lilith")

        self.root.resizable(width=False, height=False)

        paddedMain = Frame(self.root)
        paddedMain.grid(padx=5, pady=5, stick=E+W+N+S)

        recievedGrid = Frame(paddedMain)
        recievedGrid.grid(padx=0)

        self.RMessages = Text(recievedGrid, bg="white", state=DISABLED)
        self.RMessages.pack()

        sendingGrid = Frame(paddedMain)
        sendingGrid.grid()

        self.SMessageText = Entry(sendingGrid, width=63)
        self.SMessageText.grid(row=0, column=0, sticky=W)
        self.SMessageText.bind("<Return>", self.handleSend)

        sendButton = Button(sendingGrid, text="Send", command=self.handleSend)
        sendButton.grid(row=0, column=1, sticky=E)

    def _initServer(self, port):
        self.backend = Backend(self.RMessages, self.handleRecieve, port)
        self.backend.start()

    def handleRecieve(self, output, msg):
        output.config(state=NORMAL)
        output.insert("end", msg+"\n")
        output.config(state=DISABLED)

    def handleSend(self, event=None):
        message = self.SMessageText.get()
        self.SMessageText.delete(0, END)
        self.frontend.send(message)

def main():
  root = Tk()
  app = ChatClient(root, 9000, 8000)
  root.mainloop()

if __name__ == '__main__':
  main()
