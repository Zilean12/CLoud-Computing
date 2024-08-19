from google_auth_oauthlib.flow import InstalledAppFlow

#client_secrets.json file
credentials_file = 'C:/Users/aryan/OneDrive - st.niituniversity.in/t/client_secrets.json'

# Explicitly list scopes to match those in the OAuth process
scopes = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/drive.file'
]

# Create an InstalledAppFlow object from the credentials file
flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes=scopes)

# Starts a local server to handle the authentication flow
creds = flow.run_local_server(port=0)

# Print the access token and confirm access
print(f'Access token: {creds.token}')
print("Access granted to Google Drive, Profile, and Email.")

