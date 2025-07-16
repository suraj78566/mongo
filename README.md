# MongoDB Integration Setup Guide for JIO TV+ Bot

## Prerequisites

1. **MongoDB Atlas Account**: Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. **Cloudflare Worker**: Your existing worker deployment

## Step 1: Set Up MongoDB Atlas

### 1.1 Create a Free Cluster
1. Sign up/login to MongoDB Atlas
2. Create a new project (e.g., "JioTV Bot")
3. Build a free cluster (M0 Sandbox)
4. Choose your preferred cloud provider and region
5. Name your cluster (e.g., "Cluster0")

### 1.2 Create Database User
1. Go to Database Access
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username and strong password
5. Grant "Read and Write to any database" privileges
6. Add user

### 1.3 Configure Network Access
1. Go to Network Access
2. Click "Add IP Address"
3. Choose "Allow Access from Anywhere" (0.0.0.0/0)
4. Confirm

### 1.4 Enable Data API
1. Go to Data API in the left sidebar
2. Click "Enable Data API"
3. Create an API Key:
   - Give it a name (e.g., "JioTV Bot API Key")
   - Copy and save the API key securely
4. Note your Data API URL (it looks like: `https://data.mongodb-api.com/app/data-xxxxx/endpoint/data/v1`)

## Step 2: Configure Cloudflare Worker Environment Variables

Go to your Cloudflare Worker dashboard and add these environment variables:

```
MONGODB_DATA_API_URL = https://data.mongodb-api.com/app/data-xxxxx/endpoint/data/v1
MONGODB_API_KEY = your-api-key-here
MONGODB_DATA_SOURCE = Cluster0
MONGODB_DATABASE = jiotv_bot
```

## Step 3: Database Schema

The bot will automatically create these collections:

### Users Collection
```json
{
  "_id": "auto-generated",
  "userId": "telegram-user-id",
  "firstName": "John",
  "lastName": "Doe",
  "username": "johndoe",
  "languageCode": "en",
  "joinedAt": "2025-01-16T10:30:00.000Z",
  "lastActive": "2025-01-16T15:45:00.000Z"
}
```

### Interactions Collection
```json
{
  "_id": "auto-generated",
  "userId": "telegram-user-id",
  "action": "new_user|message|channel_view",
  "timestamp": "2025-01-16T10:30:00.000Z",
  "command": "/start",
  "channelKey": "optional-channel-key"
}
```

## Step 4: Key Features Added

### 🔄 Persistent User Storage
- Users are now stored permanently in MongoDB
- Bot remembers users even after worker restarts

### 📊 Enhanced Analytics
- Track user interactions
- Monitor channel usage
- Store user registration data

### 🎯 Improved Broadcasting
- Broadcast to all users from database
- Better error handling
- Accurate user counts

### 📈 Rich Statistics
- Real user count from database
- Activity tracking
- Usage analytics

## Step 5: Admin Commands Enhanced

### `/stats` - Enhanced Statistics
Now shows:
- Real user count from MongoDB
- Total channels loaded
- Number of categories

### `/broadcast <message>` - Database-Powered Broadcasting
- Sends to all users in MongoDB
- Better error tracking
- Accurate delivery reports

### New Potential Commands (for future):
```javascript
// You can add these commands later:
// /users - Show detailed user statistics
// /active - Show recent active users
// /usage - Show channel usage statistics
```

## Step 6: Benefits of MongoDB Integration

### ✅ Data Persistence
- No data loss on worker restarts
- Permanent user storage
- Historical data tracking

### ✅ Scalability
- Handle unlimited users
- Fast database operations
- Cloud-based reliability

### ✅ Analytics
- User behavior tracking
- Channel popularity metrics
- Growth analytics

### ✅ Advanced Features
- User segmentation
- Targeted messaging
- Usage patterns

## Step 7: Testing the Integration

1. Deploy your updated worker code
2. Start a conversation with your bot
3. Check MongoDB Atlas dashboard:
   - Go to Collections
   - You should see `users` and `interactions` collections
   - New users should appear automatically

## Step 8: Monitoring

### MongoDB Atlas Dashboard
- Monitor database usage
- View collection statistics
- Check API usage

### Cloudflare Worker Logs
- Monitor for any database errors
- Check successful operations
- Debug connection issues

## Troubleshooting

### Common Issues:

1. **"MongoDB not properly configured" error**
   - Check environment variables are set correctly
   - Verify API key is valid
   - Confirm Data API is enabled

2. **Connection timeouts**
   - Check network access settings
   - Verify IP whitelist includes 0.0.0.0/0
   - Confirm cluster is running

3. **API key errors**
   - Regenerate API key if needed
   - Check API key permissions
   - Verify Data API URL is correct

### Debug Tips:
- Use console.log() in your worker to debug
- Check Cloudflare Worker real-time logs
- Monitor MongoDB Atlas logs

## Cost Considerations

### MongoDB Atlas Free Tier (M0):
- 512 MB storage
- Shared RAM and vCPU
- No time limit
- Perfect for small to medium bots

### Data API Usage:
- Free tier: 1,000 requests/day
- Additional requests: $0.10 per 1,000
- Monitor usage in Atlas dashboard

## Security Best Practices

1. **Environment Variables**: Store all sensitive data in Cloudflare environment variables
2. **API Key**: Never commit API keys to code
3. **Network Access**: Consider restricting to specific IPs in production
4. **Database User**: Use least privilege principle for database users

## Next Steps

With MongoDB integrated, you can now:
- Track user growth over time
- Analyze channel popularity
- Implement user preferences
- Add premium features
- Create user segments for targeted messaging

Your bot now has enterprise-grade data persistence! 🚀
