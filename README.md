# Underwriting Workbench Backend

A FastAPI-based backend for processing insurance submissions from emails with attachments.

## Features

- 📧 Email intake from Logic Apps with attachment processing
- 📄 Multi-format document parsing (PDF, DOCX, XLSX, Images)
- 🔍 OCR support for scanned documents
- 🤖 LLM-powered structured data extraction
- 📊 PostgreSQL database with SQLAlchemy ORM
- 🚀 FastAPI with automatic API documentation
- 📝 Comprehensive logging and error handling

## Architecture

1. **Logic Apps** → `/api/email/intake` (emails + attachments)
2. **Document Parsing** → Extract text from various file formats
3. **LLM Processing** → Extract structured insurance data
4. **Database Storage** → Save drafts and confirmed submissions
5. **Work Assignment** → Round-robin assignment to underwriters

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google Gemini API key
- Tesseract OCR (for image processing)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.template .env
   # Edit .env with your Retool database URL and Gemini API key
   ```
4. Initialize the database:
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Email Processing
- `POST /api/email/intake` - Process incoming emails from Logic Apps
- `GET /api/submissions/draft/{id}` - Retrieve submission draft
- `POST /api/submissions/confirm/{id}` - Confirm and finalize submission

### Data Management
- `GET /api/submissions/draft` - List all drafts
- `GET /api/submissions` - List confirmed submissions
- `GET /api/work-items` - List work items
- `GET /health` - Health check

## Project Structure

```
email-parsing-uw/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy models
│   ├── database.py      # Database configuration
│   ├── parsers.py       # Document parsing utilities
│   └── llm.py          # LLM integration
├── uploads/            # Uploaded attachments
├── requirements.txt    # Dependencies
├── .env.template      # Environment variables template
└── README.md          # This file
```

## Document Parsing Support

- **PDF**: Text extraction + OCR fallback for scanned docs
- **DOCX**: Full text and table extraction
- **XLSX**: Multi-sheet data extraction
- **Images**: OCR with Tesseract (JPG, PNG, TIFF, BMP)

## LLM Integration

Extracts structured insurance data:
- Insured Name
- Policy Type
- Coverage Amount
- Effective Date
- Broker Information

Supports:
- Google Gemini models (primary)
- Extensible for OpenAI, Azure OpenAI

## Database Schema

- `email_intake`: Raw email data
- `submission_draft`: Extracted data drafts
- `submissions`: Confirmed submissions
- `work_items`: Assigned underwriter tasks

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows Python best practices with:
- Type hints
- Comprehensive logging
- Error handling
- Modular architecture

## 🚀 Vercel Deployment

This application is ready for serverless deployment on Vercel:

### Quick Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/email-parsing-uw)

### Manual Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard:
# - DATABASE_URL (your Retool database URL)
# - GEMINI_API_KEY (your Google AI API key)
# - GEMINI_MODEL=gemini-2.5-flash
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Production Features
- ✅ **Serverless**: Scales automatically with Vercel
- ✅ **Database**: Connected to Retool PostgreSQL
- ✅ **LLM**: Google Gemini integration
- ✅ **Document Parsing**: PDF, DOCX, XLSX support
- ⚠️ **OCR**: Disabled in serverless (use cloud OCR services if needed)

⚠️ **Security Note**: Never commit your `.env` file or database credentials to version control. Always use environment variables for sensitive configuration.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License