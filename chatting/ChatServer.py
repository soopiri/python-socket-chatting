import socket
from _thread import *
from tkinter import *


def insert_chatlog(msg):
    chat_log['state'] = 'normal'
    chat_log.insert("end", f'{msg}\n')
    chat_log['state'] = 'disabled'

def threaded(client_socket, addr):
    global chat_log
    insert_chatlog(f"Connected by : {c_list_to_name[str(addr[1])]}")
    for c in c_list:
        c.sendall(('[System] ' + c_list_to_name[str(addr[1])] + ' 님이 접속하였습니다.').encode())
    while 1:
        try:
            data = client_socket.recv(1024)
            insert_chatlog(f"Received from [{c_list_to_name[str(addr[1])]}] ({addr[0]}:{str(addr[1])}) : {str(data.decode())}")
            for c in c_list:
                c.sendall((c_list_to_name[str(addr[1])] + ' : ' + data.decode()).encode())
        except ConnectionResetError as e:
            c_list.remove(client_socket)
            for c in c_list:
                c.sendall(('[System] '+ c_list_to_name[str(addr[1])] + ' 님이 나갔습니다.').encode())
            insert_chatlog(f"Disconnected by [{c_list_to_name[str(addr[1])]}] ({addr[0]}:{str(addr[1])})")
            del c_list_to_name[str(addr[1])]
            break
    client_socket.close()

def server_open():
    HOST = ip_entry.get(); PORT = int(port_entry.get())
    start_new_thread(make_server,(HOST,PORT))
    open_button['state'] = 'disabled'
    ip_entry['state'] = 'readonly'
    port_entry['state'] = 'readonly'

def server_close():
    exit()

def make_server(HOST, PORT):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 포트사용중이라 연결할 수 없다는 WinError 10048 에러를 해결하기 위해 필요합니다.
    # 서버 소켓의 SOL_SOCKET의 SO_REUSEADDR(이미 사용중인 포트에 대해서도 바인드 허용) 를 1(True)로 설정하는 것으로 이해
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen()
    insert_chatlog('Server Start')

    while 1:
        is_duplicated = False
        client_socket, addr = server_socket.accept()
        nickname = str(client_socket.recv(1024).decode()).replace("IDREGIST::", "")
        for value in c_list_to_name.values():
            if value == nickname:
                is_duplicated = True
            if is_duplicated:
                client_socket.send(("DUPLICATED_NAME: 종료 후 다시 실행해주세요.").encode())
        else:
            c_list.append(client_socket)
            c_list_to_name[str(addr[1])] = nickname
            start_new_thread(threaded, (c_list[-1], addr))

c_list = []
c_list_to_name = {}
close = False
server_socket = None

s_root = Tk()
s_root.geometry('500x500')
s_root.title('Private Chatting Server')
s_root.resizable(False, False)

''' Top Menu '''
Label(s_root, text = 'Server IP : ').place(x=20, y=20)
Label(s_root, text = 'Port : ').place(x=250, y=20)
ip_entry = Entry(s_root, width=14, text = '127.0.0.1'); ip_entry.place(x=83, y=21)
ip_entry.insert(0,'127.0.0.1')
port_entry = Entry(s_root, width=5, text = '9999'); port_entry.place(x = 290, y=21)
port_entry.insert(0,'9999')
open_button = Button(s_root,text='Server Open', command=server_open); open_button.place(x=380, y=18)

''' Middle Menu '''
chat_log = Text(s_root, width = 65, height = 29, state = 'disabled', spacing2 = 2) ; chat_log.place(x=20, y=60)

''' Bottom Menu '''
close_button = Button(s_root,text='Server Close',command=server_close); close_button.place(x=200, y = 460)
s_root.mainloop()
