import zmq, sys

class ChatServer():
    def __init__(self, input_port, output_port):
        ctx = zmq.Context()
        self.input = ctx.socket(zmq.PULL)
        self.input.bind('tcp://*:'+str(input_port))
        self.output = ctx.socket(zmq.PUB)
        self.output.bind('tcp://*:'+str(output_port))

    def run(self):
        while True:
            message = self.input.recv()
            print message
            self.output.send(message)
        pub.close()
        pull.close()

def main():
    server = ChatServer(8000, 9000)
    print "Input  8000"
    print "Output 9000"
    server.run()

if __name__ == '__main__':
    main()
