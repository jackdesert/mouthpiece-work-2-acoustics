from warcio.archiveiterator import ArchiveIterator
from html2text import html2text
import re
import mailparser
import json
from pathlib import Path
import quopri
import shutil
import email
import ipdb
from pydoc import help as ph

# Path to your .warc file
warc_file_path = '/Users/saundraraney/Downloads/mouthpiecework.UdewYP7.warc'

HTML_DIR = Path('html')
NON_SLUG_CHARS = re.compile(r'[^a-z0-9]')
SPACE = ' '
HYPHEN = '-'
SEPARATOR = '---------------------------'

# Delete and recreate html directory
# so it's fresh each time
shutil.rmtree(str(HTML_DIR), ignore_errors=True)
HTML_DIR.mkdir(parents=True, exist_ok=True)

# There are about 12_000 posts
ZFILL = 5

# Only set this to small for fast iteration
MAX = 10

def plain(text):
    """
    Return the plain text part of an email body

    Adapted from https://pythonhint.com/post/9826809957529457/parsing-multipart-emails-in-python-and-saving-attachments
    """
    # Replace &quot; with double quote
    # Because otherwise when splitting on semicolon inside `headers['Content-Type']`,
    # the splitting happens incorrectly because there are
    text = text.replace('&quot;', '"')
    msg = mailparser.parse_from_string(text)
    if msg.defects:
        err = f'Defects found while parsing message: {msg.defects}'
        # We ignore super long messages that have defects because the first
        # one we found was a digest over 50_000 characters
        if len(text) > 10_000:
            return err
        # run it twice through conversion to make sure it takes
        body = html2text(html2text(msg.body))
        return f'{err}\n\n{body}'
    if len(msg.text_plain) > 0:
        return SEPARATOR.join(msg.text_plain)
    elif len(msg.text_html) > 0:
        # process twice with html2text to make sure it takes
        return f'This html message parsed with html2text {SEPARATOR}' + html2text(html2text(SEPARATOR.join(msg.text_html)))
    elif len(msg.body) == 0:
        return '(No message body found for this email)'
    else:
        ipdb.set_trace()
        1
        return ''


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

class Message:
    __slots__ = ('meta','body', 'children')
    def __init__(self, *, meta):
        self.meta = meta
        self.body = None
        self.children = []

    @property
    def subject(self):
        return self.meta['subject']

    def __repr__(self):
        return f'Message ({self.subject})'


parents = {}
subject_mapping = {}
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
            body = body.replace('&gt;', '>')
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
            message.body = body
            #print(body)
            #print('\n')
        else:
            # This happens first
            #print(content)
            this_id = content['messageId']
            parent_id = content['topicFirstRecord']

            message = Message(meta=content)

            # For some reason parent_id is zero when it is the parent
            if parent_id == 0:
                parent_id = this_id
                # Only need parents in mapping
                subject = content['subject']
                subject_mapping[parent_id] = slugify(subject)
                parents[parent_id] = message
            else:
                parents[parent_id].children.append(message)

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

ipdb.set_trace()
1
