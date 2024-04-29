import email
import json
import quopri
import re
import shutil
from pathlib import Path
from pydoc import help as ph
from collections import defaultdict
from datetime import datetime
import ipdb

import mailparser
from html2text import html2text
from jinja2 import Environment, FileSystemLoader
from warcio.archiveiterator import ArchiveIterator

# Only set this to small for fast iteration
MAX = 2000_000

INDEX_TITLE = 'Mouthpiece Work Yahoo Group'
INDEX_SUBTITLE = 'The human readable archive'
SOURCE_CODE = 'https://github.com/jackdesert/mouthpiece-work'

# Create a Jinja2 environment
ENV = Environment(loader=FileSystemLoader('templates'))

# Path to your .warc file
WARC_FILE_PATH = 'warc/mouthpiecework.UdewYP7.warc.gz'

HTML_DIR = Path('threads')
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
        return f'This html message parsed with html2text {SEPARATOR}' + html2text(
            html2text(SEPARATOR.join(msg.text_html))
        )
    elif len(msg.body) == 0:
        return '(No message body found for this email)'
    else:
        raise ValueError('No Appropriate message body')


class Message:
    __slots__ = ('meta', 'body', 'children')

    def __init__(self, *, meta):
        self.meta = meta
        self.body = None
        self.children = []

    @property
    def subject(self):
        return self.meta['subject']

    @property
    def meta_json(self):
        """
        Return meta as well-formatted json
        """
        return json.dumps(self.meta, indent=4)
    @property
    def id_(self):
        return self.meta['messageId']

    @property
    def filename_if_parent(self):
        """
        Remove non-url-friendly chars

        Only use this if it is a parent
        """
        text = self.subject.lower().strip()
        text = NON_SLUG_CHARS.sub(SPACE, text)
        text = text.strip()
        text = text.replace(SPACE, HYPHEN)
        id_zfilled = str(self.id_).zfill(ZFILL)
        return f'{id_zfilled}__{text}.html'

    @property
    def author_short(self):
        return self.meta['yahooAlias']

    @property
    def author(self):
        alias = self.meta['yahooAlias']
        author_ = self.meta['author']
        return f'{alias} ({author_})'

    def __repr__(self):
        return f'Message ({self.subject})'


def build_parents():
    parents = {}
    all_messages = []
    # Open the .warc file
    with open(WARC_FILE_PATH, 'rb') as warc_file:
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
                    # ValueError: string argument should contain only ASCII characters
                    # Not sure why we get this sometimes
                    pass
                message.body = body
            else:
                this_id = content['messageId']
                parent_id = content['topicFirstRecord']
                all_messages.append(this_id)

                message = Message(meta=content)

                # For some reason parent_id is zero when it is the parent
                if parent_id == 0:
                    parent_id = this_id
                    # Only need parents in mapping
                    subject = content['subject']
                    parents[parent_id] = message
                else:
                    try:
                        parents[parent_id].children.append(message)
                    except KeyError:
                        # Not sure why we are missing parent with id 6560, 6863
                        # So we create a surrogate parent...note the subject will contain RE
                        print(f'WARNING: Creating surrogate parent for {parent_id}')
                        parents[parent_id] = Message(
                            meta={**content, 'messageId': parent_id}
                        )

    return parents


def write_index(parents):
    parents_by_year = defaultdict(list)
    for parent in parents.values():
        year = datetime.utcfromtimestamp(parent.meta['date']).year
        parents_by_year[year].append(parent)

    template = ENV.get_template('index.html')
    context = dict(
        parents_by_year=parents_by_year,
        title=INDEX_TITLE,
        subtitle=INDEX_SUBTITLE,
        source_code=SOURCE_CODE,
    )
    html = template.render(context)
    with open('index.html', 'w') as writer:
        writer.write(html)


def write_html_threads(parents):
    template = ENV.get_template('thread.html')
    for parent_id_, parent in parents.items():
        context = dict(
            title=INDEX_TITLE,
            parent=parent,
            messages=[parent, *parent.children],
            source_code=SOURCE_CODE,
        )
        html = template.render(context)
        with open(HTML_DIR / parent.filename_if_parent, 'w') as writer:
            writer.write(html)


if __name__ == '__main__':
    parents_ = build_parents()
    write_html_threads(parents_)
    write_index(parents_)
