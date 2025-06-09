import re
from urllib.parse import urlparse
from utils.parental_controls import load_parental_controls

# List of profane words to filter
profanity = []

def is_safe_url(url, safe_mode=True):
    """
    Check if a URL is safe by verifying its format and domain.
    Returns False if the URL is in the blocked list and safe mode is enabled.
    Otherwise, it returns True.
    """
    if not safe_mode:
        return True  # Allow all URLs if safe mode is disabled
    
    # Reload settings each time to get latest blocked sites
    settings = load_parental_controls()
    blocked_websites = settings.get("blocked_websites", [])
    allowed_websites = settings.get("allowed_websites", [])
    
    parsed_url = urlparse(url)
    
    if not parsed_url.scheme in ("http", "https"):
        return False  # Invalid URL scheme
    
    # Normalize netloc (convert to lowercase and remove 'www.')
    domain = parsed_url.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]  # Remove 'www.'

    # Check if the domain is in blocked_websites
    for blocked_site in blocked_websites:
        blocked_domain = blocked_site.lower()
        if blocked_domain.startswith("www."):
            blocked_domain = blocked_domain[4:]
        if domain == blocked_domain or domain.endswith("." + blocked_domain):
            return False

    return True  # Safe if not blocked



