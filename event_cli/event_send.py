"""
Sends an event from command line
"""

# TODO: Estimate Fees
# TODO: Do the actual send from the privkey
# TODO: Check the sender has rights before sending

import sys
import base64


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 event_send.py EVT text='your_text_message'")
        print("Usage: python3 event_send.py EVT file='path/to/file'")
    _, event_name, content = sys.argv
    #print(content)
    type = content[:4].upper()
    content = content[5:]
    if type == 'FILE':
        with open(content, 'rb') as fp:
            content = fp.read()
            message = base64.b85encode(content).decode("utf-8")
    elif type == 'TEXT':
        message = base64.b85encode(content.encode('utf-8')).decode("utf-8")
    else:
        raise ValueError("Type has to be text or file")
        sys.exit()
    print("Message:", 'event:msg:'+event_name+':'+message)
    clear = base64.b85decode(message.encode('utf-8')).decode("utf-8")
    print(clear)