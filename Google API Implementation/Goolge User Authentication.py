from google_auth_oauthlib.flow import InstalledAppFlow

# Replace with your downloaded credentials file path
credentials_file = 'client_secrets.json'

# Scopes define what data your application can access
scopes = [ 'openid','https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

# Creates an InstalledAppFlow object from the credentials file
flow = InstalledAppFlow.from_client_secrets_file(
    credentials_file,
    scopes=scopes
)

# Starts a local server to handle the authentication flow in your browser
creds = flow.run_local_server(port=0)

# Print the access token after successful login
print(f'Access token: {creds.token}')