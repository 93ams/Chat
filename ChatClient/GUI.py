from Tkinter import *
import json
import tkMessageBox
from ChatClient import ChatClient

DEBUG = False

class GUI(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.__root = root

        self.__username = ""

        self.__init_interface()
        self.__client = ChatClient(self.__handleRecieve)
        self.__root.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def is_registered(self):
        return self.__client.is_registered()

    def __init_interface(self):
        self.__root.title("Chat")

        self.__root.resizable(width=False, height=False)

        paddedMain = Frame(self.__root)
        paddedMain.grid(padx=5, pady=5, stick=E+W+N+S)

        settingsGrid = Frame(paddedMain)
        settingsGrid.grid(sticky=E+W+N)

        nameGrid = Frame(settingsGrid)
        nameGrid.grid(row=0, column=0, sticky=E+N+S)

        self.__nameVar = StringVar()
        nameLabel = Label(nameGrid, text = "Username: ")
        nameLabel.grid(row=0, column=0, sticky= W+N+S)
        self.__nameField  = Entry(nameGrid, width=16, textvariable=self.__nameVar)
        self.__nameField.grid(row=0, column=1, sticky=N+S)
        self.__nameField.bind("<Return>", self.__handleSetName)
        self.__nameButton = Button(nameGrid, text="Set", width=3, command=self.__handleSetName)
        self.__nameButton.grid(row=0, column=2, sticky=E+N+S)
        self.__nameField.bind("<Return>", self.__handleSetName)

        roomGrid = Frame(settingsGrid)
        roomGrid.grid(row=0, column=1, sticky=W+N+S)

        self.__roomVar = StringVar()
        roomLabel = Label(roomGrid, text = "  RoomID: ")
        roomLabel.grid(row=0, column=0, sticky= W+N+S)
        self.__roomField = Entry(roomGrid, width=15, textvariable=self.__roomVar, state=DISABLED)
        self.__roomField.grid(row=0, column=1, sticky=W+N+S)
        self.__roomField.bind("<Return>", self.__handleJoinRoom)
        self.__JoinRoomButton = Button(roomGrid, text="Join", width=3, command=self.__handleJoinRoom, state=DISABLED)
        self.__JoinRoomButton.grid(row=0, column=2, sticky=N+S)
        self.__JoinRoomButton.bind("<Return>", self.__handleJoinRoom)
        self.__LeaveRoomButton = Button(roomGrid, text="Leave", width=4, command=self.__handleLeaveRoom, state=DISABLED)
        self.__LeaveRoomButton.grid(row=0, column=3, sticky=E+N+S)
        self.__LeaveRoomButton.bind("<Return>", self.__handleLeaveRoom)

        recievedGrid = Frame(paddedMain)
        recievedGrid.grid(padx=0)

        self.__RMessages = Text(recievedGrid, bg="white", state=DISABLED)
        self.__RMessages.pack()

        sendingGrid = Frame(paddedMain)
        sendingGrid.grid()

        self.__SMessageText = StringVar()
        self.__SMessageField = Entry(sendingGrid, width=63, textvariable=self.__SMessageText, state=DISABLED)
        self.__SMessageField.grid(row=0, column=0, sticky=W)
        self.__SMessageField.bind("<Return>", self.__handleSend)

        self.__sendButton = Button(sendingGrid, text="Send", command=self.__handleSend, state=DISABLED)
        self.__sendButton.grid(row=0, column=1, sticky=E)

    def __handleRecieve(self, msg):
        self.__RMessages.config(state=NORMAL)
        self.__RMessages.insert("end", msg+"\n")
        self.__RMessages.config(state=DISABLED)

    def __handleSend(self, event = None):
        if self.__client.is_connected():
            message = self.__SMessageText.get()
            self.__SMessageText.set("")
            self.__client.send_message(message)

    def __handleLeaveRoom(self, event = None):
        if self.__client.is_registered():
            if self.__client.is_connected():
                try:
                    self.__client.leave_room()
                    self.__roomField.config(state=NORMAL)
                    self.__JoinRoomButton.config(state=NORMAL)
                    self.__LeaveRoomButton.config(state=DISABLED)
                    self.__SMessageField.config(state=DISABLED)
                    self.__sendButton.config(state=DISABLED)
                except:
                    pass

    def __handleJoinRoom(self, event = None):
        RoomID = self.__roomVar.get()
        if RoomID != "":
            if self.__client.is_registered():
                self.__current_room = RoomID
                try:
                    self.__client.enter_room(RoomID)
                    self.__roomField.config(state=DISABLED)
                    self.__JoinRoomButton.config(state=DISABLED)
                    self.__LeaveRoomButton.config(state=NORMAL)
                    self.__SMessageField.config(state=NORMAL)
                    self.__sendButton.config(state=NORMAL)
                except:
                    pass
        else:
            tkMessageBox.showwarning("Error", "Invalid RoomID!")

    def __handleSetName(self, event=None):
        name = self.__nameVar.get()
        if name != "":
            self.__username = name
            try:
                self.__client.register_to_nameserver(name)
                self.__nameField.config(state=DISABLED)
                self.__nameButton.config(state=DISABLED)
                self.__roomField.config(state=NORMAL)
                self.__JoinRoomButton.config(state=NORMAL)
            except:
                pass
        else:
            tkMessageBox.showwarning("Error", "Invalid Username!")

    def __on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            if self.__client.is_registered():
                if self.__client.is_connected():
                    self.__client.leave_room()
                self.__client.unregister()
            self.__root.destroy()

def main():
    root = Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
