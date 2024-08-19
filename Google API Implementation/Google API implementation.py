from tkinter import *
from tkinter import messagebox, filedialog
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle
import os
import io
from googleapiclient.http import MediaIoBaseDownload

class LoginApp:
    def __init__(self):
        self.root = Tk()
        self.root.title("Cloud-Computing-Lab01")
        self.root.geometry("925x500+300+200")
        self.root.configure(bg='#fff')
        self.root.resizable(False, False)
        
        self.credentials = None
        self.folder_id = None

        image = PhotoImage(file='C:/Users/aryan/OneDrive - st.niituniversity.in/t/05.png')
        Label(self.root, image=image, bg='white').place(x=50, y=50)

        self.frame = Frame(self.root, width=350, height=350, bg='white')
        self.frame.place(x=480, y=70)

        self.heading = Label(self.frame, text='Sign In', fg='#57a1f8', bg='white', font=('Microsoft YaHei UI Light', 23, 'bold'))
        self.heading.place(x=100, y=5)

        # Button for Google login
        self.login_button = Button(self.frame, width=20, pady=7, text='Login with Google', bg='#dd4b39', fg='white', border=0, command=self.authenticate)
        self.login_button.place(x=85, y=100)

        # Buttons for Drive operations
        self.upload_button = Button(self.frame, width=20, pady=7, text='Upload File', bg='#57a1f8', fg='white', border=0, command=self.upload_file)
        self.read_button = Button(self.frame, width=20, pady=7, text='Read File', bg='#57a1f8', fg='white', border=0, command=self.read_file)
        self.delete_button = Button(self.frame, width=20, pady=7, text='Delete File', bg='#57a1f8', fg='white', border=0, command=self.delete_file)
        self.find_button = Button(self.frame, width=20, pady=7, text='Find File', bg='#57a1f8', fg='white', border=0, command=self.find_file)
        self.logout_button = Button(self.frame, width=20, pady=7, text='Logout', bg='#dd4b39', fg='white', border=0, command=self.logout)

        self.root.mainloop()

# Google OAuth 
    def authenticate(self):
        if not self.credentials or not self.credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', ['https://www.googleapis.com/auth/drive'])
            self.credentials = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
        
        drive_service = build('drive', 'v3', credentials=self.credentials)
        query = "mimeType='application/vnd.google-apps.folder' and trashed=false and name='Google Drive GUI'"
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
    
        if not items:
            folder_metadata = {'name': 'Google Drive GUI', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            self.folder_id = folder.get('id')
        else:
            self.folder_id = items[0]['id']

        # Hide the login button and show the other buttons after successful login
        self.login_button.place_forget()
        self.heading.config(text='Logged In')

        # Arrange buttons for better visibility
        self.upload_button.place(x=85, y=100)
        self.read_button.place(x=85, y=150)
        self.delete_button.place(x=85, y=200)
        self.find_button.place(x=85, y=250)
        self.logout_button.place(x=85, y=300)  # Ensure this button is visible

# Upload file 
    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            drive_service = build('drive', 'v3', credentials=self.credentials)
            file_metadata = {'name': os.path.basename(file_path), 'parents': [self.folder_id]}
            media = MediaFileUpload(file_path, resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            messagebox.showinfo("Success", f"File uploaded successfully with ID: {file.get('id')}")

# Read file
    def read_file(self):
        drive_service = build('drive', 'v3', credentials=self.credentials)
        query = f"'{self.folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            messagebox.showinfo("Info", "No files found.")
            return

        # Create a new window with Checkbuttons to display files
        read_window = Toplevel(self.root)
        read_window.title("Select File to Read")

        for item in items:
            var = BooleanVar()
            cb = Checkbutton(read_window, text=item['name'], variable=var, onvalue=True,
             offvalue=False, command=lambda name=item['name'], file_id=item['id']: 
             self.download_and_open_file(name, file_id))
            cb.pack(anchor='w', padx=20, pady=5)

# Delete file
    def delete_file(self):
        drive_service = build('drive', 'v3', credentials=self.credentials)
        query = f"'{self.folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        
        if not items:
            messagebox.showinfo("Info", "No files found.")
            return

        # Create a new window with Checkbuttons to display files
        delete_window = Toplevel(self.root)
        delete_window.title("Select File to Delete")

        for item in items:
            var = BooleanVar()
            cb = Checkbutton(delete_window, text=item['name'], variable=var, onvalue=True,
             offvalue=False, command=lambda name=item['name'], file_id=item['id']: 
             self.delete_file_by_id(name, file_id))
            cb.pack(anchor='w', padx=20, pady=5)

# Find file
    def find_file(self):
        find_window = Toplevel(self.root)
        find_window.title("Find File")

        Label(find_window, text="Enter file name:").pack(pady=10)
        file_name_entry = Entry(find_window, width=50)
        file_name_entry.pack(pady=10)


        def search_file():
            file_name = file_name_entry.get()
            if file_name:
                drive_service = build('drive', 'v3', credentials=self.credentials)
                query = f"'{self.folder_id}' in parents and trashed=false and name='{file_name}'"
                results = drive_service.files().list(q=query, fields="files(id, name)").execute()
                items = results.get('files', [])
                
                if not items:
                    messagebox.showinfo("Info", "No files found with that name.")
                else:
                    for item in items:
                        messagebox.showinfo("Found", f"File '{item['name']}' found with ID: {item['id']}")
            else:
                messagebox.showwarning("Input Error", "Please enter a file name.")

        Button(find_window, text="Find", command=search_file).pack(pady=10)


    def download_and_open_file(self, name, file_id):
        drive_service = build('drive', 'v3', credentials=self.credentials)
        request = drive_service.files().get_media(fileId=file_id)
        file_path = os.path.join(os.getcwd(), name)
        with io.FileIO(file_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
        os.startfile(file_path)

# os.startfile(file_path)  # Opens the file in the default application
    def delete_file_by_id(self, name, file_id):
        drive_service = build('drive', 'v3', credentials=self.credentials)
        drive_service.files().delete(fileId=file_id).execute()
        messagebox.showinfo("Success", f"File '{name}' deleted successfully.")


    def logout(self):
        self.credentials = None
        self.upload_button.place_forget()
        self.read_button.place_forget()
        self.delete_button.place_forget()
        self.find_button.place_forget()
        self.logout_button.place_forget()
        self.heading.config(text='Sign In')
        self.login_button.place(x=85, y=100)
        
        self.root.quit()  # Close the app

app = LoginApp()
