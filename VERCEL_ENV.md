# Vercel Environment Variables Configuration

You'll need to set these environment variables in your Vercel dashboard:

## Required Environment Variables

### Database Configuration
```
DATABASE_URL=postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require
```

### Google Gemini Configuration
```
GEMINI_API_KEY=AIzaSyAZKwC1d_krqu5d6B0j_7xxkxBAkYS0Jfw
GEMINI_MODEL=gemini-2.5-flash
MAX_TOKENS=1000
```

### Application Settings
```
UPLOAD_DIR=/tmp/uploads
LOG_LEVEL=INFO
```

### CORS Settings (Production)
```
CORS_ORIGINS=*
CORS_CREDENTIALS=true
CORS_METHODS=*
CORS_HEADERS=*
```

## How to Set Environment Variables in Vercel

1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable above with its corresponding value
5. Make sure to select the appropriate environments (Production, Preview, Development)

## Notes

- The DATABASE_URL contains your Retool database credentials
- The GEMINI_API_KEY is your Google AI API key
- The UPLOAD_DIR is set to /tmp/uploads which is writable in Vercel's serverless environment
- For production, consider restricting CORS_ORIGINS to your actual domain