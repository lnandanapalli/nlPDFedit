# PDF Chat Assistant

A modern web application that provides conversational PDF manipulation using LLM-powered natural language understanding. Built with FastAPI backend and React TypeScript frontend.

## Features

- **Natural Language PDF Operations**: Chat with an AI assistant to perform PDF operations
- **Multiple PDF Operations**: Extract text, merge, split, rotate, watermark, compress PDFs
- **Real-time Communication**: WebSocket support for instant responses
- **Modern UI**: Dark-themed React interface with Tailwind CSS
- **File Management**: Upload, download, and manage PDF files
- **Session Management**: Persistent chat sessions with file context

## Architecture

### Backend (FastAPI)
- **FastAPI**: Modern Python web framework
- **OpenAI Integration**: GPT-3.5-turbo for natural language understanding
- **PDFly**: PDF manipulation library
- **WebSocket**: Real-time communication
- **Session Management**: Persistent user sessions

### Frontend (React + TypeScript)
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Socket.io**: WebSocket client
- **Axios**: HTTP client

## 🚀 Quick Start

### Option 1: Windows Quick Start
```bash
# Double-click start.bat or run:
start.bat
```

### Option 2: Manual Setup
1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your OpenAI API key:**
```bash
# Copy example environment file
copy .env.example .env

# Edit .env and add your API key:
OPENAI_API_KEY=sk-your-actual-api-key-here
```

3. **Run the application:**
```bash
streamlit run app.py
```

4. **Open your browser to:**
```
http://localhost:8501
```

### Option 3: Full Setup Script
```bash
python setup.py
```

## 💬 Example Commands

- "Extract pages 1-5 from the uploaded PDF"
- "Merge these two PDFs together"
- "Rotate page 3 by 90 degrees"
- "Split this PDF into separate pages"
- "Compress the PDF to reduce file size"
- "Add a watermark saying 'CONFIDENTIAL'"
- "Extract all text from this PDF"

## 🏗️ Architecture

```
pdf-editor/
├── app.py                 # Main Streamlit interface
├── core/                  # Core processing engine
│   ├── pdf_dispatcher.py  # PDFly function mapping
│   └── llm_processor.py   # OpenAI integration
├── models/                # Data models
│   └── pdf_models.py      # PDF and chat objects
├── utils/                 # Utility functions
│   ├── file_utils.py      # File management
│   └── error_handling.py  # Error handling
├── examples/              # Sample workflows
│   ├── demo.py           # Demo script
│   └── example_workflows.md
└── requirements.txt       # Dependencies
```

## 🔧 Available Operations

| Operation | Description | Example Command |
|-----------|-------------|-----------------|
| **Extract Pages** | Get specific pages from a PDF | "Extract pages 1-5" |
| **Merge PDFs** | Combine multiple PDFs | "Merge all PDFs together" |
| **Split PDF** | Break PDF into separate files | "Split into individual pages" |
| **Rotate Pages** | Turn pages by degrees | "Rotate page 3 by 90 degrees" |
| **Compress** | Reduce file size | "Compress this PDF" |
| **Watermark** | Add text watermarks | "Add 'DRAFT' watermark" |
| **Extract Text** | Get text content | "Extract all text" |
| **Bookmarks** | Add navigation | "Add table of contents" |

## 🎯 Project Titles for Resume

1. **Conversational PDF Agent with LLM-Powered Understanding and Action**
2. **AI Chat Interface for Semantic PDF Manipulation**
3. **Natural Language PDF Automation via LLM and PDFly**
4. **LLM-Driven Interactive PDF Assistant**
5. **Chat-Based PDF Command Processor Using PDFly**
6. **GPT-Style PDF Manipulation Interface with Intelligent Function Calling**
7. **Multistep PDF Assistant: Conversational Control Over Documents**
8. **Prompt-to-Action PDF Tool with Context-Aware Execution**
9. **Intelligent PDF Command Line in Chat Form**
10. **AI-Powered PDF Workflow Assistant with Object-Level Reasoning**

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Web Interface)
- **Backend**: Python 3.8+
- **AI/ML**: OpenAI GPT-4 (Function Calling)
- **PDF Processing**: PDFly, PyPDF2
- **File Management**: Pathlib, UUID
- **Environment**: python-dotenv
- **Typing**: typing-extensions

## 📝 Usage Examples

### Basic Workflow
1. Upload PDF files using the sidebar
2. Select a PDF to work with
3. Type natural language commands
4. Download processed results

### Advanced Workflow
```
User: "I need to prepare this contract for review"
Assistant: "I can help with that! What preparation do you need?"

User: "Extract the first 5 pages and add a 'UNDER REVIEW' watermark"
Assistant: "I'll extract pages 1-5 and add the watermark for you."
```

### Multi-PDF Operations
```
User: "Merge all the uploaded reports together"
Assistant: "I'll combine all 3 PDF reports into a single document."

User: "Now compress the merged file"
Assistant: "I'll compress the merged PDF to reduce its file size."
```

## 🔍 Features Deep Dive

### Natural Language Processing
- Uses OpenAI GPT-4 with function calling
- Understands context and maintains conversation history
- Supports conversational commands and clarifications

### File Management
- Automatic tracking of original and generated PDFs
- Temporary file cleanup
- Support for multiple file formats and sizes

### Error Handling
- Comprehensive validation for all operations
- User-friendly error messages
- Graceful degradation and recovery

### Security
- API key management through environment variables
- File size limits and validation
- Safe file handling practices

## 🚧 Setup Requirements

- Python 3.8 or higher
- OpenAI API key (GPT-4 access recommended)
- 2GB+ available disk space for temporary files
- Modern web browser for Streamlit interface

## 📚 Documentation

- **Setup Guide**: See `setup.py` for detailed installation
- **Examples**: Check `examples/example_workflows.md`
- **Demo**: Run `python examples/demo.py`
- **API Reference**: See inline code documentation

## 🤝 Contributing

This is a demonstration project showcasing conversational AI for PDF manipulation. Feel free to:
- Fork and extend functionality
- Add new PDF operations
- Improve the UI/UX
- Add support for other LLM providers

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🆘 Troubleshooting

### Common Issues
1. **"API key not found"** - Set `OPENAI_API_KEY` in `.env` file
2. **"Cannot read PDF"** - Ensure PDF is not corrupted or password-protected
3. **"File too large"** - Check file size limits in configuration
4. **"Permission denied"** - Check file and directory permissions

### Getting Help
- Check the console output for detailed error messages
- Review `examples/example_workflows.md` for usage patterns
- Ensure all dependencies are properly installed

---

**Built with ❤️ using Python, Streamlit, and OpenAI GPT-4**