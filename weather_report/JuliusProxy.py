import socket
import re

class JuliusProxy:
    """ JuliusProxy. Connects to julius and parses the recognition result."""
    """ localhost = 0.0.0.0 """
    def __init__(self, host="localhost", port=10500):
        """ Initialize the proxy. connect to julius -module."""
        self.sock = socket.socket(socket.AF_INET,
                                socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.pattern = re.compile('([A-Z]+=".*?")')

    def getResult(self):
        """ Receive result as XML format."""
        msg = []
        # receive all messages
        while True:
            msg.append(self.sock.recv(1024))
            """ type(msg[]) = <class 'bytes'> in python3"""
            if b"</RECOGOUT>" in msg[-1]:
                break
        # connect them all, and split with \n
        """ msg[](byte)->msg[](str<utf-8>) in python3 """
        self.msg = "".join([m.decode("utf-8").replace(".\n", "") for m in msg])
        self.msg = self.msg.split("\n")
        return self.msg

    def parseResult(self):
        """ run after getResult. it parses the reseult
        and returns a dictionary having results"""

        # parse all WHYPO tags
        result = []
        for msg in [m for m in self.msg if "WHYPO" in m]:
            result.append({})

            for prop in self.pattern.findall(msg):
                key = prop.split("=")[0]
                value = prop.split('"')[1]

                if key == "CM":
                    try:
                        value = float(value)
                    except:
                        pass
                if key == "CLASSID":
                    try:
                        value = int(value)
                    except:
                        pass
                result[-1][key] = value

        return result
    def end(self):
        self.sock.send('DIE\n'.encode('utf-8'))
    def terminate(self):
        self.sock.send('TERMINATE\n'.encode('utf-8'))
    def resume(self):
        self.sock.send('RESUME\n'.encode('utf-8'))


if __name__ == "__main__":
    proxy = JuliusProxy()
    while 1:
        print("\n".join(proxy.getResult()))
        print("[")
        for result in proxy.parseResult():
            print(result)
        print("]")
