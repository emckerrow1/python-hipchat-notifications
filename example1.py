from hipchat import Hipchat

HIPCHAT_TOKEN = ''     # Hipchat API token
HIPCHAT_SERVER = None  # Hipchat Server URL (e.g. https://hipchat.example.com). Use None for default
HIPCHAT_ROOM = ''      # Hipchat room ID or name

# Create session
session = Hipchat(token=HIPCHAT_TOKEN, server_url=HIPCHAT_SERVER)

# Message object to be sent
data = {
    'message': 'Hello World - <b>Bold</b> is great.',
    'message_format': 'html',
    'color': 'green',
    'notify': True
}

# Send the notification
session.send_notification(HIPCHAT_ROOM, **data)

