import socket
import threading

class Bot:

    # __init__ runs immediately when someone invokes the Bot class
    #
    # e.g.
    #
    # bot = Bot() / bot = osu_bot_framework.Bot()
    #
    # The above would automatically run this __init__ function.
    # therefore we are using it to set up the basic information linked to a bot so that it's easy to access
    # e.g. bot.__username, bot.__password, etc...
    def __init__(self, host="irc.ppy.sh", port=6667, username="", password="", verbose=False):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__host = host
        self.__port = port
        self.__username = username
        self.__password = password
        self.__verbose = verbose

    # this method makes the bot start listening on a thread
    def start(self):
        # connect and login
        try:
            self.__sock.connect((self.__host, self.__port))
            self.__sock.sendall(("PASS " + self.__password + "\n").encode())
            self.__sock.sendall(("USER " + self.__username + "\n").encode())
            self.__sock.sendall(("NICK " + self.__username + "\n").encode())

            # you can send a join command here just to test it works but really we want a method exposed to do it
            self.__sock.sendall(("JOIN #mp_83515535\n").encode())

            # listen to messages sent back from osu
            self.__listen()
        except:
            print("There was an error connecting to", self.__host)

    def __listen(self, running=False):
        # This makes the __listen method run on an independent thread
        if not running:
            threading.Thread(target=self.__listen, args=(True,)).start()
            return

        # this is the buffer for all the data received back from osu
        buffer = ""

        #run always
        while True:
            # each loop append data to the buffer
            buffer += self.__sock.recv(2048).decode() # .decode() converts the binary to string for us

            # the data is received line by line, so we look for the new line character ('\n')
            while '\n' in buffer:
                # extract the first line
                line = buffer.split('\n')[0] + '\n'
                # remove the line from the buffer
                buffer = buffer.replace(line, "")
                # remove new line and carriage return characters
                line = line.replace('\n', '').replace('\r', '')

                # when verbose is enabled print everything we are receiving
                if self.__verbose:
                    if "QUIT :" not in line:
                        print(line)
                    

                # To make sure we are still connected, osu sends us a "PING" message every few minutes
                # to stay connected we must send back "PONG"
                if line.split(" ")[0] == "PING":

                    # send back the same exact message, except replace "PING" with "PONG"
                    self.__sock.sendall((line.replace("PING", "PONG") + '\n').encode())
                    continue


                # from here we need to think... above I am just sending back pong no matter what but maybe we wanna do what I was doing before to make sure that all messages go through a manager to stop rate limit problems... idk
