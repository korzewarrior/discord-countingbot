# How to Get Your Discord Token

This is a guide on how to safely obtain Discord user tokens for use with the automated counter system. These tokens allow the script to send messages on behalf of real Discord accounts.

## Important Warnings

⚠️ **PLEASE READ THESE WARNINGS CAREFULLY** ⚠️

1. **Never share your token with anyone you don't trust completely**
2. **Using automated user accounts (self-bots) may violate Discord's Terms of Service**
3. **Excessive or obvious automation can lead to account suspensions**
4. **Store tokens securely and never commit them to public repositories**
5. **Use this at your own risk - we take no responsibility for banned accounts**

## Method 1: Using Developer Tools in Browser

1. Open Discord in your web browser
2. Log in to the Discord account you want to use
3. Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) to open Developer Tools
4. Go to the "Network" tab in Developer Tools
5. Refresh the page by pressing `F5` (or `Cmd+R` on Mac)
6. Type `/api` in the filter box at the top
7. Click on any request to `/api/v9`
8. In the right panel, select the "Headers" tab
9. Scroll down to find "Authorization" under "Request Headers"
10. The long string next to "Authorization" is your user token

## Method 2: Using Discord Application Storage

1. Open Discord in your web browser
2. Log in to the Discord account you want to use
3. Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) to open Developer Tools
4. Go to the "Application" tab
5. In the left sidebar, expand "Local Storage" and click on "https://discord.com"
6. Type "token" in the filter box at the top
7. Look for a key that contains "token"
8. The value in quotes is your user token

## Safely Using Multiple Accounts

For the counting system to work properly, you need at least 2 accounts (to avoid the "same user counting twice in a row" rule). Here are some tips:

1. **Use separate devices or browsers** for each account to avoid login conflicts
2. **Create new accounts with unique email addresses** if needed
3. **Age your accounts** - don't use brand new accounts for automation
4. **Establish account history** by using each account normally for a while
5. **Use different IP addresses** if possible to avoid suspicion
6. **Set up separate profiles** in Chrome/Firefox for each account

## Tips for Avoiding Detection

1. **Use realistic delays** between messages (the system handles this automatically)
2. **Run during low-activity hours** (the system is configured for 1 AM - 5 AM by default)
3. **Match your usual typing speed** by adjusting the delay settings
4. **Randomize user-agent strings** for each account
5. **Take breaks occasionally** by pausing the counter
6. **Don't increase speed** as you get to higher numbers - maintain natural pacing

## Storing Tokens Safely

1. **Never commit tokens to GitHub** or other public repositories
2. **Keep tokens in a local config file** that is in your `.gitignore`
3. **Consider encrypting tokens** when stored on disk
4. **Rotate tokens** if you suspect they may be compromised
5. **Don't share the same token** across multiple applications

## Example User Agent Strings

Using a realistic user agent string helps make requests look more legitimate. Here are some examples:

### Windows Chrome
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
```

### macOS Safari
```
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15
```

### iOS
```
Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1
```

### Android
```
Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36
```

## Final Note

Remember that this approach requires using real user accounts, not bots. The system is designed to make your counting appear as natural as possible, but it's still important to be cautious and follow good security practices. 