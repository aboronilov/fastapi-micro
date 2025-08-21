# Google OAuth2 Integration

This project now includes Google OAuth2 authentication alongside the existing username/password authentication.

## Setup

### 1. Google OAuth2 Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" and create an OAuth 2.0 Client ID
5. Set the authorized redirect URI to: `http://localhost:8000/auth/oauth/google/callback`
6. Copy the Client ID and Client Secret

### 2. Environment Variables

Add the following to your `env` file:

```bash
# Google OAuth2 Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/oauth/google/callback

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API Endpoints

### OAuth2 Endpoints

- `GET /auth/oauth/google/authorize` - Get Google OAuth2 authorization URL
- `GET /auth/oauth/google/callback` - Handle OAuth2 callback (GET)
- `POST /auth/oauth/google/callback` - Handle OAuth2 callback (POST)

### Authentication Flow

1. **Get Authorization URL**: Call `GET /auth/oauth/google/authorize` to get the Google OAuth2 URL
2. **User Authorization**: Redirect the user to the returned URL
3. **Callback**: Google will redirect back to your callback URL with an authorization code
4. **Token Exchange**: The callback endpoint exchanges the code for a JWT token

## Database Changes

The following fields have been added to the `users` table:

- `google_id` - Google's unique user ID
- `avatar_url` - User's profile picture URL
- `is_oauth_user` - Flag to identify OAuth2 users
- `username` - Made nullable (OAuth2 users might not have usernames)
- `password` - Made nullable (OAuth2 users don't have passwords)

## Usage Examples

### Frontend Integration

```javascript
// 1. Get authorization URL
const response = await fetch('/auth/oauth/google/authorize');
const data = await response.json();
const authUrl = data.authorization_url;

// 2. Redirect user to Google
window.location.href = authUrl;

// 3. Handle callback (in your callback page)
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');

if (code) {
    const tokenResponse = await fetch('/auth/oauth/google/callback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code })
    });
    
    const tokenData = await tokenResponse.json();
    // Store the access token
    localStorage.setItem('access_token', tokenData.access_token);
}
```

### Testing

Use the provided `oauth_test.html` file to test the OAuth2 flow:

1. Start the application: `make start`
2. Open `oauth_test.html` in your browser
3. Click "Get Google OAuth2 URL" to get the authorization URL
4. Click "Login with Google" to start the OAuth2 flow

## Migration

Run the database migrations to add OAuth2 support:

```bash
# If running locally
make db-upgrade

# If running in Docker
make docker-migrate
```

## Security Notes

- Always use HTTPS in production
- Store sensitive configuration in environment variables
- Use a strong JWT secret key
- Consider implementing CSRF protection
- Validate the state parameter in production

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**: Make sure the redirect URI in Google Console matches exactly
2. **"Client ID not found"**: Verify your Google Client ID is correct
3. **"Database connection failed"**: Ensure the database is running and migrations are applied

### Debug Mode

To see detailed OAuth2 logs, check the application logs:

```bash
make docker-logs
```
