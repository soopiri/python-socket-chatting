import socket
from _thread import *
import threading
from tkinter import *
from time import sleep


def send(socket, nickname):
    global go_send
    global is_first
    if is_first:
        regist_msg = f"IDREGIST::{nickname.strip()}"
        socket.send(regist_msg.encode())
        is_first = False
    while True:
        try:
            if go_send:
                message = (message_input.get(1.0,"end")).rstrip()
                socket.send(message.encode())
                message_input.delete(1.0, "end")
                go_send = False
            else:
                if go_out:
                    socket.close()
                    exit()
                sleep(0.1)
        except ConnectionResetError as resetError:
            chat_log['state'] = 'normal'
            chat_log.insert("end", '\n[System] 서버가 다운되었습니다. 서버를 확인해보세요.\n')
            chat_log['state'] = 'disabled'
            exit()

def receive(socket):
    first = True
    while True:
        try:
            data = socket.recv(1024)
            chat_log['state'] = 'normal'
            if first: # 이걸 처음 체크 이후 의미없이 매번 체크하므로 이렇게 하는 건 효율적이지 않음.
                if 'DUPLICATED_NAME' in data.decode():
                    login_button['state'] = 'disabled'
                    logout_button['state'] = 'disabled'
                    send_button['state'] = 'disabled'
                chat_log.insert("end",str(data.decode()))
                first = False
            else:
                chat_log.insert("end",'\n' + str(data.decode()))
                chat_log.see('end')
                chat_log['state'] = 'disabled'
        except ConnectionAbortedError as e:
            chat_log['state'] = 'normal'
            chat_log.insert("end", '\n[System] 접속을 종료합니다.\n')
            chat_log['state'] = 'disabled'
            exit()

def login():
    # 서버의 ip주소 및 포트
    HOST = ip_entry.get()
    PORT = int(port_entry.get())
    NICKNAME = name_entry.get()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    threading.Thread(target=send, args= (client_socket, NICKNAME)).start()
    threading.Thread(target=receive, args= (client_socket,)).start()
    exit()

def try_login():
    global go_out
    NICKNAME = name_entry.get()

    if NICKNAME.strip() == '':
        chat_log['state'] = 'normal'
        chat_log.insert("end", '[System] 닉네임을 입력해주세요.\n')
        chat_log['state'] = 'disabled'
    else:
        start_new_thread(login,())
        login_button['state'] = 'disabled'
        logout_button['state'] = 'active'
        ip_entry['state'] = 'readonly'
        port_entry['state'] = 'readonly'
        name_entry['state'] = 'readonly'
        go_out = False

def try_logout():
    global go_out
    login_button['state'] = 'active'
    logout_button['state'] = 'disabled'
    ip_entry['state'] = 'normal'
    port_entry['state'] = 'normal'
    name_entry['state'] = 'normal'
    go_out = True

def set_go_send(event):
    global go_send
    go_send = True

go_out, go_send = False, False
is_first = True
c_root = Tk()
c_root.geometry('500x540')
c_root.title('Private Chatting Room')
c_root.resizable(False, False)

''' Top Menu '''
Label(c_root, text = 'Server IP : ').place(x=20, y=20)
ip_entry = Entry(c_root, width=15)
ip_entry.place(x=83, y=21)
ip_entry.insert(0,'127.0.0.1')
Label(c_root, text = 'Port : ').place(x=20, y=45)
port_entry = Entry(c_root, width=15)
port_entry.place(x = 83, y=46)
port_entry.insert(0,'9999')
Label(c_root, text = 'Name: ').place(x=20, y=70)
name_entry = Entry(c_root, width=15)
name_entry.place(x=83, y=71)



login_button = Button(c_root,text='Log In', command=try_login); login_button.place(x=400, y=35)
logout_button = Button(c_root,text='Log Out',state = 'disabled', command = try_logout); logout_button.place(x=400, y=65)

''' Middle Menu '''
chat_frame = Frame(c_root)
scrollbar = Scrollbar(chat_frame) ; scrollbar.pack(side='right',fill='y')
chat_log = Text(chat_frame, width = 62, height = 24, state = 'disabled', yscrollcommand = scrollbar.set) ; chat_log.pack(side='left')#place(x=20, y=60)
scrollbar['command'] = chat_log.yview
chat_frame.place(x=20, y=100)
message_input = Text(c_root, width = 55, height = 4) ; message_input.place(x=20,y = 430)
send_button = Button(c_root, text = 'Send', command = lambda: set_go_send(None)); send_button.place(x=430, y=445)
message_input.bind("<Return>",set_go_send)

''' Bottom Menu '''
close_button = Button(c_root,text='Close',command=exit); close_button.place(x=200, y = 500)

c_root.mainloop()