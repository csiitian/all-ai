import html, re, markdown

def clean_html(html_text):
    """
    Converts HTML content to plain text.
    Removes tags, converts entities (like `&lt;` to `<`), and keeps formatting simple.
    """
    # Unescape HTML entities like &lt; &gt; &quot;
    plain_text = html.unescape(html_text)
    # Remove HTML tags (keep inner text only)
    plain_text = re.sub(r'<[^>]+>', '', plain_text)
    # Remove excessive newlines and whitespace
    plain_text = re.sub(r'\n+', '\n', plain_text).strip()
    return plain_text

def markdown_to_plain_text(md_text):
    """
    Converts Markdown content to plain text.
    Handles code blocks, headings, and formatting gracefully.
    """
    # Convert Markdown to HTML, then remove tags (to keep formatting intact)
    html_from_md = markdown.markdown(md_text)
    plain_text = clean_html(html_from_md)
    return plain_text
