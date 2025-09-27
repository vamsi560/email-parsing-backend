# 🚀 Vercel Deployment Guide

This guide will help you deploy your Underwriting Workbench FastAPI backend to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm i -g vercel`
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## 🔧 Deployment Steps

### 1. **Initialize Vercel Project**
```bash
# In your project directory
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - Project name? email-parsing-uw (or your preferred name)
# - Directory? ./
# - Override settings? No
```

### 2. **Set Environment Variables**
In your Vercel dashboard (or via CLI):

```bash
# Database
vercel env add DATABASE_URL
# Paste: postgresql://retool:npg_yf3gdzwl4RqE@ep-silent-sun-afdlv6pj.c-2.us-west-2.retooldb.com/retool?sslmode=require

# Gemini API
vercel env add GEMINI_API_KEY
# Paste: AIzaSyAZKwC1d_krqu5d6B0j_7xxkxBAkYS0Jfw

vercel env add GEMINI_MODEL
# Paste: gemini-2.5-flash

vercel env add MAX_TOKENS
# Paste: 1000

# Application settings
vercel env add UPLOAD_DIR
# Paste: /tmp/uploads

vercel env add LOG_LEVEL
# Paste: INFO
```

### 3. **Deploy**
```bash
# Deploy to production
vercel --prod
```

## 🔗 **Your API Endpoints**

After deployment, your API will be available at:
- **Base URL**: `https://your-project-name.vercel.app`
- **API Docs**: `https://your-project-name.vercel.app/docs`
- **Health Check**: `https://your-project-name.vercel.app/health`

### Main Endpoints:
- `POST /api/email/intake` - Email processing from Logic Apps
- `GET /api/submissions/draft/{id}` - Get submission draft
- `POST /api/submissions/confirm/{id}` - Confirm submission
- `GET /api/submissions/draft` - List all drafts
- `GET /api/submissions` - List all submissions
- `GET /api/work-items` - List work items

## 🧪 **Testing Your Deployment**

### Test Health Endpoint:
```bash
curl https://your-project-name.vercel.app/health
```

### Test Email Intake:
```bash
curl -X POST https://your-project-name.vercel.app/api/email/intake \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Insurance Submission",
    "from": "test@example.com",
    "received_at": "2025-09-27T06:00:00Z",
    "body": "Test insurance submission with policy details",
    "attachments": []
  }'
```

## ⚙️ **Configuration Notes**

### Serverless Limitations:
- **File Storage**: Uses `/tmp/uploads` (temporary, files are deleted after function execution)
- **OCR**: Disabled (Tesseract not available in serverless environment)
- **Database**: Connected to your Retool PostgreSQL (persistent)
- **Function Timeout**: 30 seconds max (configured in vercel.json)

### For Production Use:
1. **File Storage**: Consider using cloud storage (AWS S3, Google Cloud Storage) for persistent file storage
2. **OCR**: Use cloud OCR services (Google Vision API, AWS Textract) if needed
3. **CORS**: Update CORS settings to restrict to your actual frontend domain
4. **Rate Limiting**: Consider adding rate limiting for production use

## 🔄 **Continuous Deployment**

Once connected to your Git repository:
- **Automatic deploys** on push to main branch
- **Preview deployments** for pull requests
- **Custom domains** can be configured in Vercel dashboard

## 🐛 **Troubleshooting**

### Check Deployment Logs:
```bash
vercel logs https://your-project-name.vercel.app
```

### Common Issues:
1. **Import Errors**: Make sure all dependencies are in requirements.txt
2. **Database Connection**: Verify DATABASE_URL environment variable
3. **API Key**: Check GEMINI_API_KEY is set correctly
4. **Cold Starts**: First request may be slower (serverless cold start)

## 📱 **Logic Apps Integration**

Update your Logic Apps to use the new Vercel URL:
```
https://your-project-name.vercel.app/api/email/intake
```

Your Underwriting Workbench backend is now live and scalable! 🎉