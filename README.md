# ChatEDA - EDA Documentation Assistant

ChatEDA is an intelligent chat interface designed specifically for EDA (Electronic Design Automation) documentation. It allows users to upload PDF documentation and ask questions about EDA tools, receiving context-aware responses based on the uploaded content.

## Features

- PDF document upload and processing
- Intelligent text chunking and retrieval
- Support for both local and remote LLM APIs
- Interactive chat interface
- Context-aware responses
- Customizable system prompts
- Temperature control for response creativity

## Installation

1. Clone the repository:
```bash
git clone git@github.com:1571859588/ChatEDA.git
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Set the following environment variables:
- `HF_HOME`: Directory for storing Hugging Face models (e.g., "D:\\Research")
- For remote API: Set your API key in the code or as environment variable

### Local Model Setup

1. Update the model path in `local_model_server.py`:
```python
MODEL_PATH = "path/to/your/local/model"
```

2. Start the local model server:
```bash
python local_model_server.py
```

## Usage

1. Start the Streamlit app:
```bash
streamlit run "Chatbot_app - no apikey.py"
```

2. Access the web interface at `http://localhost:8501`

3. Upload PDF documentation files:
   - Click "上传PDF文件" in the sidebar
   - Select one or more PDF files
   - Wait for processing and vectorization

4. Choose API endpoint:
   - "远程API": Uses remote API (requires API key)
   - "本地API": Uses local model server

5. Select model:
   - For remote API: Choose from available models
   - For local API: Uses local model

6. Start chatting:
   - Type your questions about EDA tools
   - Receive context-aware responses based on uploaded documentation

## Architecture

The system consists of three main components:

1. **Document Processing**
   - PDF text extraction
   - Text chunking using RecursiveCharacterTextSplitter
   - Vector embeddings using HuggingFace models
   - FAISS vector store for efficient retrieval

2. **Local Model Server**
   - FastAPI-based server
   - Supports local LLM models
   - Compatible with OpenAI API format

3. **Chat Interface**
   - Streamlit-based web interface
   - Real-time streaming responses
   - Context management
   - PDF upload and processing

## Limitations

- PDF processing may be slow for large documents
- Local model requires significant computational resources
- Maximum context length depends on chosen model
- Remote API requires valid API key and internet connection

## Troubleshooting

1. **Memory Issues**
   - Reduce chunk size in `split_text()`
   - Use smaller models
   - Process fewer documents simultaneously

2. **Model Loading Issues**
   - Ensure correct model path
   - Check GPU memory availability
   - Verify model compatibility

3. **API Errors**
   - Verify API key
   - Check internet connection
   - Confirm API endpoint availability

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.