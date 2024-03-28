import tkinter as tk
from tkinter import messagebox, simpledialog
from ftplib import FTP

def connect_to_ftp():
    global ftp

    server = server_entry.get()
    port = int(port_entry.get())
    username = username_entry.get()
    password = password_entry.get()

    try:
        ftp = FTP()
        ftp.connect(server, port)
        ftp.login(username, password)
        log_text.insert(tk.END, "Connected to FTP server\n")
        list_files()
    except Exception as e:
        log_text.insert(tk.END, f"Error connecting to FTP server: {str(e)}\n")
        messagebox.showerror("Error", str(e))

def list_files():
    global ftp
    files = ftp.nlst()
    log_text.insert(tk.END, "\nLIST OF FILES:\n")
    for file in files:
        log_text.insert(tk.END, f"{file}\n")
    log_text.insert(tk.END, "\nLIST OF FILES END\n")

def retrieve_file():
    global ftp
    filename = filename_entry.get()
    try:
        lines = []
        ftp.retrlines("RETR " + filename, lines.append)
        log_text.insert(tk.END, '\nRETR FILE\n')
        for line in lines:
            log_text.insert(tk.END, line + '\n')
        log_text.insert(tk.END, "\nRETR FILE END\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error retrieving file: {str(e)}\n")
        messagebox.showerror("Error", str(e))

def create_file():
    global ftp
    filename = filename_entry.get()
    file_content = simpledialog.askstring("Enter File Content", "Enter the content of the file:")
    
    try:
        with open(filename, "w") as file:
            file.write(file_content)
        with open(filename, "rb") as file:
            ftp.storbinary(f"STOR {filename}", file)

        log_text.insert(tk.END, f"FILE {filename} CREATED.\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error creating file: {str(e)}\n")
        messagebox.showerror("Error", str(e))

def update_file():
    global ftp
    filename = filename_entry.get()
    
    try:
        with open(filename, "wb") as file:
            ftp.retrbinary(f"RETR {filename}", file.write)
        
        with open(filename, "r") as file:
            file_content = file.read()

        updated_content = simpledialog.askstring("Update File Content", "Update the content of the file:", initialvalue=file_content)
        
        with open(filename, "w") as file:
            file.write(updated_content)
        
        with open(filename, "rb") as file:
            ftp.storbinary(f"STOR {filename}", file)
        
        log_text.insert(tk.END, f"FILE {filename} UPDATED.\n")
        
    except Exception as e:
        log_text.insert(tk.END, f"Error creating file: {str(e)}\n")
        messagebox.showerror("Error", str(e))


def delete_file():
    global ftp
    filename = filename_entry.get()
        
    try:
        ftp.delete(filename)
        log_text.insert(tk.END, f"FILE {filename} DELETED.\n")
    except Exception as e:
        log_text.insert(tk.END, f"Error deleting file: {str(e)}\n")
        messagebox.showerror("Error", str(e))



root = tk.Tk()
root.geometry("1000x1000")
root.title("FTP Client")

server = tk.StringVar() 
server.set('ftp.dlptest.com')
server_label = tk.Label(root, text="Server:")
server_entry = tk.Entry(root, textvariable=server)

port = tk.StringVar() 
port.set('21')
port_label = tk.Label(root, text="Port:")
port_entry = tk.Entry(root, textvariable=port)

username = tk.StringVar() 
username.set('dlpuser')
username_label = tk.Label(root, text="Username:")
username_entry = tk.Entry(root, textvariable=username)

password = tk.StringVar() 
password.set('rNrKYTX9g7z3RgJRmxWuGHbeu')
password_label = tk.Label(root, text="Password:")
password_entry = tk.Entry(root, show="*", textvariable=password)

connect_button = tk.Button(root, text="Connect", command=connect_to_ftp)
list_button = tk.Button(root, text="List Files", command=list_files)

filename_label = tk.Label(root, text="Filename:")
filename_entry = tk.Entry(root)

retrieve_button = tk.Button(root, text="Retrieve File", command=retrieve_file)
create_button = tk.Button(root, text="Create File", command=create_file)
delete_button = tk.Button(root, text="Delete File", command=delete_file)
update_button = tk.Button(root, text="Update File", command=update_file)


server_label.place(x=100, y=20)
server_entry.place(x=200, y=20)
port_label.place(x=400, y=20)
port_entry.place(x=500, y=20)
username_label.place(x=100, y=60)
username_entry.place(x=200, y=60)
password_label.place(x=400, y=60)
password_entry.place(x=500, y=60)
connect_button.place(x=300, y=100)
list_button.place(x=400, y=100)
filename_label.place(x=250, y=140)
filename_entry.place(x=350, y=140)
retrieve_button.place(x=200, y=180)
create_button.place(x=300, y=180)
delete_button.place(x=400, y=180)
update_button.place(x=500, y=180)

log_text = tk.Text(root, height=40, width=75)
log_text.place(x=200, y = 220)

root.mainloop()