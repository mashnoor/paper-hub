import re
from flask import current_app
from PyPDF2 import PdfReader
import requests
import json


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages[:5]:  # First 5 pages only
            text += page.extract_text()
        return text[:5000]  # Limit to 5000 chars
    except Exception as e:
        current_app.logger.error(f"Error extracting PDF text: {e}")
        return ""


def extract_metadata_openrouter(text, api_key):
    """Extract paper metadata using OpenRouter API"""
    print(f"Extracting metadata with API key: {api_key}")
    if not api_key:
        current_app.logger.warning("No OpenRouter API key provided")
        # Basic extraction without API
        return extract_metadata_basic(text)
    
    try:
        # OpenRouter API implementation
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "github.com/mashnoor/paper-hub",
                "X-Title": "PaperHub"
            },
            json={
                "model": "deepseek/deepseek-chat-v3-0324:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts metadata from academic papers. Return a JSON object with keys: title, authors, abstract, journal."
                    },
                    {
                        "role": "user",
                        "content": f"Extract the title, authors, and abstract from this academic paper text. Return ONLY a JSON object:\n\n{text[:3000]}"
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
        )
        
        print(f"OpenRouter API status: {response.status_code}")
        print(f"OpenRouter API response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from the response
            try:
                # Find JSON in the response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    metadata = json.loads(json_match.group())
                    
                    # Convert authors list to string
                    authors = metadata.get('authors', 'Unknown')
                    if isinstance(authors, list):
                        authors = ", ".join(authors)

                    return {
                        "title": metadata.get('title', 'Untitled Paper'),
                        "authors": authors,
                        "abstract": metadata.get('abstract', ''),
                        "journal": metadata.get('journal', None)
                    }
            except json.JSONDecodeError:
                pass
                
    except Exception as e:
        current_app.logger.error(f"OpenRouter API error: {e}")
    
    # Fallback to basic extraction
    return extract_metadata_basic(text)


def extract_metadata_basic(text):
    """Basic metadata extraction without API"""
    lines = text.split('\n')
    title = lines[0] if lines else "Untitled Paper"
    
    # Try to find abstract
    abstract = ""
    abstract_start = text.lower().find("abstract")
    if abstract_start != -1:
        abstract_end = text.lower().find("introduction", abstract_start)
        if abstract_end == -1:
            abstract_end = text.lower().find("1.", abstract_start)
        if abstract_end == -1:
            abstract_end = abstract_start + 1000
        
        abstract = text[abstract_start:abstract_end].strip()
        # Remove "abstract" word and clean up
        abstract = re.sub(r'^abstract\s*', '', abstract, flags=re.IGNORECASE)
        abstract = re.sub(r'\s+', ' ', abstract).strip()
    
    # Try to find authors (usually after title, before abstract)
    authors = "Unknown"
    title_end = text.find('\n')
    if title_end != -1 and abstract_start != -1:
        potential_authors = text[title_end:abstract_start].strip()
        # Look for lines that might contain author names
        author_lines = []
        for line in potential_authors.split('\n')[:5]:  # Check first 5 lines after title
            # Simple heuristic: lines with commas or "and" might be author lists
            if (',' in line or ' and ' in line.lower()) and len(line) < 200:
                author_lines.append(line.strip())
        if author_lines:
            authors = ' '.join(author_lines)
    
    return {
        "title": title[:500],
        "abstract": abstract[:1000],
        "authors": authors[:500],
        "journal": None
    } 