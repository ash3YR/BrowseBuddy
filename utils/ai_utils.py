import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Load the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

def fetch_page_text(url):
    """Extracts visible text from a page (basic)."""
    response = requests.get(url, timeout=3)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text(separator=' ', strip=True)

def classify_text_content(text):
    """Classifies text into safe/unsafe categories."""
    candidate_labels = ["educational", "entertainment", "adult", "violent", "news"]
    result = classifier(text[:1000], candidate_labels)  # Limit to 1000 chars
    top_label = result["labels"][0]
    return top_label
