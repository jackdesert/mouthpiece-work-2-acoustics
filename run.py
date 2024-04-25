from warcio.archiveiterator import ArchiveIterator
import json
from pathlib import Path
import quopri
import ipdb

# Path to your .warc file
warc_file_path = '/Users/saundraraney/Downloads/mouthpiecework.UdewYP7.warc'

HTML_DIR = Path('html')
def build_filename(*, parent_id, this_id):
    """
    Where to write the data
    """
    dir_ = HTML_DIR / str(parent_id)
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_ / f'{this_id}.html'

def append_to_file(*, content:str, fname:Path):
    with fname.open('a') as appender:
        appender.write(content)


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
            # Remove the `=\n` in email bodies
            body = quopri.decodestring(body).decode('utf8')
            append_to_file(fname=fname, content=body)
            #print(body)
            #print('\n')
        else:
            # This happens first
            #print(content)
            this_id = content['messageId']
            parent_id = content['topicFirstRecord']
            fname = build_filename(parent_id=parent_id, this_id=this_id)
            append_to_file(fname=fname, content=f'\n\n===========================================\n{content}')
            #topicNextRecord = content['topicNextRecord']
            #topicPrevRecord = content['topicPrevRecord']


        # Do something with the URL and content
        #print("URL:", url)
        #print("Content:", content)

print(types)
