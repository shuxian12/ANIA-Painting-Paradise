import socket
import threading
import pickle
import re
# import json

class whiteBoardServer:
    clients_list = []
    last_received_data = ""
    preX, preY = None, None

    def __init__(self):
        self.server_socket = None
        self.create_server()

    def create_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_ip = '127.0.0.1'
        local_port = 48763
        self.server_socket.setsockopt(      #允許重複使用本地地址及接口
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((local_ip, local_port))
        print("listening for incoming details")
        self.server_socket.listen(20)
        self.receive_data_in_new_thread()

    def receive_data_in_new_thread(self):
        t = None
        while 1:
            client = so, (ip, port) = self.server_socket.accept()
            self.add_to_clients_list(client)
            print("connected to ", ip, ":", str(port))
            t = threading.Thread(target=self.receive_data, args=(so,))
            t.start()

    def add_to_clients_list(self, client):
        if client not in self.clients_list:
            self.clients_list.append(client)

    def receive_data(self, so):
        while 1:
            incoming_buffer = so.recv(2048)
            if not incoming_buffer:
                break
            r_data = pickle.loads(incoming_buffer)
            if r_data == 'close':
                for client in self.clients_list:
                    if client[0] == so:
                        self.clients_list.remove(client)

                break

            if r_data.get('mission') == 1:
                server_data = {'mission': 1}
                if re.search("傷心",r_data.get('message')) or re.search("心情不好",r_data.get('message')):  #:你傷心了嗎？ 你可以跟我說說你的心事，我會盡力幫助你的。
                    server_data.update({'username': "server", 'message': "當全世界都不要你的時候，請記得還有我，我也不要你,要好好活下去，因為每天都有新的打擊\n"})
                    so.send(pickle.dumps(server_data))
                elif re.search("開心",r_data.get('message')):
                    server_data.update({'username': "server", 'message': "我也很開心，因為我不是你，但你確定你做完作業了嗎？\n"})
                    so.send(pickle.dumps(server_data))
                elif re.search("好難",r_data.get('message')):
                    server_data.update({'username': "server", 'message': "我也覺得好難，但是我不是你，天下無難事，只要肯放棄\n"})
                    so.send(pickle.dumps(server_data))
                elif re.search("好累",r_data.get('message')):
                    server_data.update({'username': "server", 'message': "你琴棋書畫不會，洗衣做飯嫌累，你還是不要出門，不然會被人笑死\n"})
                    so.send(pickle.dumps(server_data))
            self.last_received_data = r_data
            # print(self.last_received_data)
            self.broadcast_to_all_clients(so)
        so.close()

    def broadcast_to_all_clients(self, so):
        for client in self.clients_list:
            sock, (ip, port) = client
            # print(ip, port)
            if sock is not so:
                # print('in')
                # sock.send(json.dumps(self.last_received_data).encode('utf-8'))
                sock.send(pickle.dumps(self.last_received_data))


if __name__ == "__main__":
    whiteBoardServer()