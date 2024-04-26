from warcio.archiveiterator import ArchiveIterator
import re
import json
from pathlib import Path
import quopri
import ipdb

# Path to your .warc file
warc_file_path = '/Users/saundraraney/Downloads/mouthpiecework.UdewYP7.warc'

HTML_DIR = Path('html')
NON_SLUG_CHARS = re.compile(r'[^a-z0-9]')
SPACE = ' '
HYPHEN = '-'

def build_filename(*, parent_id, this_id):
    """
    Where to write the data
    """
    subject_slug = subject_mapping.get(parent_id, 'unknown')
    parent_slug = f'{parent_id}__{subject_slug}'
    dir_ = HTML_DIR / parent_slug
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_ / f'{this_id}.html'

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
    for record in ArchiveIterator(warc_file):
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
            subject = content['subject']
            subject_mapping[this_id] = slugify(subject)
            fname = build_filename(parent_id=parent_id, this_id=this_id)
            append_to_file(fname=fname, content=f'\n\n===========================================\n{content}')
            #topicNextRecord = content['topicNextRecord']
            #topicPrevRecord = content['topicPrevRecord']

            # There are attachments listed, but the urls no longer work (yimg.com)
            # attachments = content['attachments']


        # Do something with the URL and content
        #print("URL:", url)
        #print("Content:", content)

print(types)
