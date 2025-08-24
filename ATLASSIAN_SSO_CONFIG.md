# Atlassian SSO Authentication Configuration

Since you're using Entra SSO (Microsoft Azure AD) for Atlassian authentication, here are the configuration options for the Atlassian tools.

## Authentication Methods Supported

The updated `AtlassianAuthManager` supports multiple authentication methods:

### 1. SSO/Session-Based Authentication (Recommended for Entra SSO)

Set these environment variables:
```bash
ATLASSIAN_AUTH_METHOD=sso
JIRA_BASE_URL=https://yourcompany.atlassian.net
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki
ATLASSIAN_SESSION_TOKEN=your_session_jwt_token
# OR
ATLASSIAN_COOKIES=session_cookie_string
```

### 2. OAuth 2.0 Authentication

Set these environment variables:
```bash
ATLASSIAN_AUTH_METHOD=oauth
JIRA_BASE_URL=https://yourcompany.atlassian.net
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki  
ATLASSIAN_OAUTH_TOKEN=your_oauth_access_token
```

### 3. API Token Authentication (Fallback)

Set these environment variables:
```bash
ATLASSIAN_AUTH_METHOD=token
JIRA_BASE_URL=https://yourcompany.atlassian.net
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki
ATLASSIAN_API_TOKEN=your_api_token
ATLASSIAN_EMAIL=your_email@company.com
```

## For Entra SSO Setup

Since you're using Entra SSO, you have a few options:

### Option 1: Extract Session Token from Browser
1. Log into Atlassian via SSO in your browser
2. Open Developer Tools > Network tab
3. Make an API request and capture the Authorization header
4. Set `ATLASSIAN_SESSION_TOKEN` to the Bearer token value

### Option 2: Extract Session Cookies
1. Log into Atlassian via SSO in your browser  
2. Open Developer Tools > Application/Storage > Cookies
3. Copy the relevant session cookies
4. Set `ATLASSIAN_COOKIES` to the cookie string

### Option 3: Service Account with API Token
1. Create a service account in your Atlassian org
2. Generate an API token for the service account
3. Use token-based authentication as fallback

## Testing Authentication

The tools will now:
- Log a warning if no authentication is configured
- Still attempt API calls (some might work without auth for testing)
- Use proper headers/cookies based on your auth method

## Current Behavior

Without authentication configured, the tools will:
- Return basic headers for testing purposes
- Log warnings about missing auth
- Allow you to see the tool structure and responses

Would you like me to help you set up one of these authentication methods based on your specific Entra SSO setup?