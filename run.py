from warcio.archiveiterator import ArchiveIterator
import re
import json
from pathlib import Path
import quopri
import shutil
import email
import ipdb

# Path to your .warc file
warc_file_path = '/Users/saundraraney/Downloads/mouthpiecework.UdewYP7.warc'

HTML_DIR = Path('html')
NON_SLUG_CHARS = re.compile(r'[^a-z0-9]')
SPACE = ' '
HYPHEN = '-'

# Delete and recreate html directory
# so it's fresh each time
shutil.rmtree(str(HTML_DIR), ignore_errors=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)

# There are about 12_000 posts
ZFILL = 5

# Only set this to small for fast iteration
MAX = 50#0_000

def plain(text):
    """
    Return the plain text part of an email body
    """
    msg = email.message_from_string(text)

    # Initialize variable to store plain text
    plain_text = ""

    # Iterate through the message parts
    for part in msg.walk():
        # Check if the part is plain text
        if part.get_content_type() == 'text/plain':
            # Append the plain text to the variable
            plain_text += part.get_payload()

    return plain_text

def build_filename(parent_id):
    """
    Where to write the data
    """
    subject_slug = subject_mapping.get(parent_id, 'unknown')
    parent_id_filled = str(parent_id).zfill(ZFILL)
    # Store as a text file so it shows line feeds
    parent_slug = f'{parent_id_filled}__{subject_slug}.txt'
    return HTML_DIR / parent_slug

def append_to_file(*, content:str, fname:Path):
    with fname.open('a') as appender:
        appender.write(content)

def slugify(text):
    """
    Remove non-url-friendly chars
    """
    text = text.lower().strip()
    text = NON_SLUG_CHARS.sub(SPACE, text)
    text = text.strip()
    text = text.replace(SPACE, HYPHEN)
    return text

subject_mapping = {}
types = set()
# Open the .warc file
with open(warc_file_path, 'rb') as warc_file:
    # Iterate over the records in the .warc file
    count = 0
    for record in ArchiveIterator(warc_file):
        count += 1
        if count > MAX:
            break
        # Get the URL of the response
        # Headers of interest include:
        headers = record.rec_headers

        url = headers.get_header('WARC-Target-URI')
        date = headers.get_header('WARC-Date')
        # Get the content of the response
        content_bytes = record.content_stream().read()

        # These appear to come in pairs.
        # First there is a JSON blob describing the content
        # Then the next record is the (email?) body
        # probably json
        content = json.loads(content_bytes.decode())
        if 'rawEmail' in content:
            body = content['rawEmail']
            body = plain(body)
            try:
                # Remove the `=\n` in email bodies
                body = quopri.decodestring(body).decode()
            except UnicodeDecodeError:
                # Sometimes this fails...perhaps because utf8 is the wrong encoding..
                pass
            except ValueError:
                #ValueError: string argument should contain only ASCII characters
                # Not sure why we get this sometimes
                pass
            append_to_file(fname=fname, content=body)
            #print(body)
            #print('\n')
        else:
            # This happens first
            #print(content)
            this_id = content['messageId']
            parent_id = content['topicFirstRecord']

            # For some reason parent_id is zero when it is the parent
            if parent_id == 0:
                parent_id = this_id
                # Only need parents in mapping
                subject = content['subject']
                subject_mapping[parent_id] = slugify(subject)

            fname = build_filename(parent_id)
            append_to_file(fname=fname, content=f'\n\n===================================\n{content}\n----------------------------------\n')
            #topicNextRecord = content['topicNextRecord']
            #topicPrevRecord = content['topicPrevRecord']

            # There are attachments listed, but the urls no longer work (yimg.com)
            # attachments = content['attachments']


        # Do something with the URL and content
        #print("URL:", url)
        #print("Content:", content)


lines = ['<h1>Hello</h1>', '<ol>']
for parent_id_, subject_ in subject_mapping.items():
    fname_ = build_filename(parent_id_)
    lines.append(f'<li><a href="../{fname_}" target="_blank">{subject_}</a></li>')
lines.append('</ol>')

with open('html/index.html', 'w') as writer:
    writer.write('\n'.join(lines))
