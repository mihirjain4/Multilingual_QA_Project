# 🌍 Multilingual Document Q&A System

## 🎯 Objective

Build a full web-based application where a user can upload any PDF document (10-15 pages) and ask questions in any language. The system must answer correctly based on the content inside the PDF.

## ✨ Features

- 🌐 Multilingual Support: Supports 8+ languages including English, Hindi, Gujarati, Marathi, Tamil, Bengali, Kannada, and Telugu
- 📄 PDF Processing: Extract and analyze text from uploaded PDF documents
- 🤖 AI-Powered Q&A: Uses Groq's Llama model for accurate question answering
- 🔄 Automatic Translation: Seamlessly translates questions and answers between languages
- 🔍 Context-Aware: Retrieves relevant context from documents to provide accurate answers
- 📊 Visual Interface: Clean Streamlit-based web interface with real-time previews
- 💰 100% FREE

## 📁 Project Structure
```text
/MihirShah_ArgyleEnigma_Assignment/
│
├──/Multilingual_QA_Project/
│
├── /src/
│   ├── app.py              # Main Streamlit application
│   ├── backend.py          # Core processing logic
│   ├── config.py           # API configuration
│   └── requirements.txt    # Python dependencies
│
├── /sample_pdfs/           # sample PDF (10-15 pages each)
│   ├── sample_pdf.pdf
│
├── /screenshots/           # Application screenshots
│   ├── upload_interface.png
│   ├── question_asking.png
│   └── answer_display.png
│
└── README.md              # Project documentation
```


## 🔧 Technical Stack

|    Component   |      Technology     |
|----------------|---------------------|
|Frontend        |     Streamlit       |
|PDF Processing  |     PyPDF2          |
|AI Model        |   Groq(Llama-70b)   |
|Embeddings      |SentenceTransformers |
|Translation     |Google Translator API|
|Similarity      |  Cosine Similarity  |



## 🚀 Quick Start

### 1. Create Virtual Environment:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies:

```bash
Clone or download the project files
pip install -r requirements.txt
```

### 3. Get API Key

- Go to [console.groq.com](https://console.groq.com)
- Sign up (FREE, no credit card)
- Create API key
- Copy it

### 4. Set up your Groq API key:

Open `src/config.py` and replace "GROQ_API_KEY" with your actual API key:
```python
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

### 5. Run the application

```bash
streamlit run src/app.py
```

That's it! Open `http://localhost:8501` in your browser.


## 🎨 Output Features

### ✅ Upload Section

- PDF Name: Display uploaded filename
- Text Preview: First 300 characters of extracted text
- Processing Status: Real-time feedback during PDF processing

### ✅ Question & Answer Section
- Language Detection: Shows detected language of user's question
- Translated Question: English version of the original question
- AI Answer: Original answer generated in English
- Final Answer: Translated answer in user's selected language
- Context Snippets: Top relevant passages from PDF with similarity scores

## 🎥 Usage Instructions

### Step 1: Upload PDF Document
<p align="center">
<img src="https://github.com/mihirjain4/Multilingual_QA_Project/blob/main/screenshots/Upload_PDF.png" alt="Upload_PDF" />
</p>
- Click the "Upload PDF" button in the main interface
- Select your PDF file (10-15 pages recommended)
- System automatically extracts and displays text preview
- View the first 300 characters of extracted text for verification

### Step 2: Select Language & Ask Question
📸 Screenshot Select Language: screenshots\Select _Language.png
📸 Screenshot Ask Question : screenshots\Ask_Question.png

- Use the sidebar dropdown to select your preferred language
- Type your question in the text area in ANY supported language
- Click the "Ask" button to process your question

### Step 3: View Multilingual Results
📸 Screenshot: screenshots\Translate_answer.png

- System processes your question through the complete pipeline
- View comprehensive results including:
- Detected Language: Original language of your question
- Translated Question: English version for processing
- AI Answer: Generated answer in English
- Final Answer: Translated answer in your selected language
- Context Snippets: Relevant PDF passages with similarity scores

## 🐛 Common Issues
→ Ensure PDF contains extractable text (not scanned images)
→ Verify Groq API key is correctly set in config.py
→ Check internet connection for translation services
→ For large PDFs, allow extra processing time


## 📝 License

MIT License - Free to use for any project!

## 👨‍💻 Author
 Mihir Shah
📧 Email: mihir.shah011@gmail.com

---

⭐ Star this repo if you found it helpful!
