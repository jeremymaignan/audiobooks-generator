import ebooklib
import nltk
from ebooklib import epub
import re
from bs4 import BeautifulSoup

#nltk.download('punkt_tab')

def clean_string(str):
    return re.sub(r'\s+', ' ', str).replace('\t', ' ').replace('\n', ' ').replace('——', ' ')

def is_roman_numeral(s):
    roman_numeral_pattern = r"^(M{0,3})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
    return bool(re.fullmatch(roman_numeral_pattern, s))

def is_chapter_title(str):
    return str and ("chapter " in str.lower() or is_roman_numeral(str))

def split_text_into_sentences(text):
    """Splits text into sentences using NLTK."""
    return nltk.sent_tokenize(text)


def parse_html_to_dict(epub_path):
    """Extracts chapters and their content from an EPUB file."""
    # Read the EPUB file
    book = epub.read_epub(epub_path, {"ignore_ncx": True})
    parsed_dict = {}

    # Access the documents in the EPUB (usually the chapters)
    toc = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    volume_title = None
    chapter_title = None
    for item in toc:
        if item.get_name().endswith('.xhtml') or item.get_name().endswith('.html'):
            # Get the body content of the EPUB chapter and convert it to a string
            content = item.get_body_content()
            content = content.decode('utf-8')  # Decode the bytes to string

            # Use BeautifulSoup to parse the content of the EPUB chapter
            soup = BeautifulSoup(content, 'html.parser')

            # Extract volume and chapter information
            if soup.find('h2') and "VOLUME" in soup.find('h2').get_text():
                volume_title = clean_string(soup.find('h2').get_text()).capitalize()
                #print(volume_title)
                # Initialize the volume dictionary if not already done
                if volume_title not in parsed_dict:
                    parsed_dict[volume_title] = {}
            if volume_title and soup.find('h3') and "chapter" in soup.find('h3').get_text().lower():
                chapter_title = clean_string(soup.find('h3').get_text())
                #print(chapter_title)
            #print("vol", volume_title, "chapt", chapter_title)
            sentences = [clean_string(p.get_text()) for p in soup.find_all('p') if 'footnote' not in p.get('class', [])]
            print(sentences)

            if volume_title and chapter_title and sentences:
                parsed_dict[volume_title][chapter_title] = []
                for s in sentences:
                    parsed_dict[volume_title][chapter_title] += split_text_into_sentences(s)

    return parsed_dict

def extract_chapters_from_epub(epub_path):
    """Extracts chapters and their content from an EPUB file."""
    book = epub.read_epub(epub_path, {"ignore_ncx": True})
    chapters = {}

    # Access the documents in the EPUB (usually the chapters)
    toc = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
    for item in toc:
        if item.get_name().endswith('.xhtml') or item.get_name().endswith('.html'):
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')
            # Example: identifying chapters by <h1>, <h2> tags or similar
            for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                chapter_title = tag.get_text()
                if is_chapter_title(chapter_title):  # Avoid empty titles
                    # Initialize a list to store the content of the chapter
                    chapter_content = []

                    # Get all siblings after the chapter title tag until the next chapter title
                    for sibling in tag.find_next_siblings():
                        if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # Stop at the next chapter heading
                            if is_chapter_title(sibling.get_text()):
                                break
                        chapter_content.append(sibling.get_text())

                    sentences = split_text_into_sentences(' '.join(chapter_content).strip())
                    # Store the chapter title and content
                    chapters[clean_string(chapter_title)] = sentences
    return chapters
