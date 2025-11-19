import sqlite3

conn = sqlite3.connect('wedcraft.db')
cursor = conn.cursor()

print('=== ALL EVENTS WITH EVENT_NAME ===')
cursor.execute('SELECT id, event_name, bride_name, groom_name, wedding_date FROM events ORDER BY id DESC LIMIT 5')
events = cursor.fetchall()
for event in events:
    event_id, event_name, bride_name, groom_name, wedding_date = event
    print(f'Event {event_id}: event_name="{event_name}", bride_name="{bride_name}", groom_name="{groom_name}", date={wedding_date}')

conn.close()