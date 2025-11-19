import sqlite3

conn = sqlite3.connect('wedcraft.db')
cursor = conn.cursor()

print('=== TOTAL RSVP RESPONSES ===')
cursor.execute('SELECT COUNT(*) FROM rsvp_responses')
total_rsvps = cursor.fetchone()[0]
print(f'Total RSVP responses in database: {total_rsvps}')

print('\n=== RSVP RESPONSES BY EVENT ===')
cursor.execute('''
SELECT r.event_id, COUNT(*) as count, e.bride_name, e.groom_name, e.user_id
FROM rsvp_responses r
LEFT JOIN events e ON r.event_id = e.id
GROUP BY r.event_id
ORDER BY r.event_id
''')
results = cursor.fetchall()
for row in results:
    event_id, count, bride_name, groom_name, user_id = row
    event_name = f'{bride_name} & {groom_name}' if bride_name and groom_name else 'Unknown Event'
    print(f'Event ID {event_id}: {count} responses - {event_name} (User ID: {user_id})')

print('\n=== EVENTS BY USER ===')
cursor.execute('SELECT user_id, COUNT(*) as event_count FROM events GROUP BY user_id')
user_events = cursor.fetchall()
for user_id, event_count in user_events:
    print(f'User ID {user_id}: {event_count} events')

print('\n=== RSVP RESPONSES WITH JOIN (Current Query) ===')
cursor.execute('''
SELECT COUNT(*) 
FROM rsvp_responses r
JOIN events e ON r.event_id = e.id
WHERE e.user_id = 1
''')
joined_count = cursor.fetchone()[0]
print(f'RSVP responses for User ID 1 (with join): {joined_count}')

print('\n=== ORPHANED RSVP RESPONSES ===')
cursor.execute('''
SELECT COUNT(*) 
FROM rsvp_responses r
LEFT JOIN events e ON r.event_id = e.id
WHERE e.id IS NULL
''')
orphaned_count = cursor.fetchone()[0]
print(f'RSVP responses with no matching event: {orphaned_count}')

print('\n=== ALL USERS ===')
cursor.execute('SELECT id, name, email FROM users')
users = cursor.fetchall()
for user_id, name, email in users:
    print(f'User ID {user_id}: {name} ({email})')

print('\n=== SAMPLE RSVP RESPONSES ===')
cursor.execute('''
SELECT r.id, r.event_id, r.family_name, r.attendance, e.user_id, e.bride_name, e.groom_name
FROM rsvp_responses r
LEFT JOIN events e ON r.event_id = e.id
LIMIT 10
''')
sample_rsvps = cursor.fetchall()
for rsvp in sample_rsvps:
    rsvp_id, event_id, family_name, attendance, user_id, bride_name, groom_name = rsvp
    print(f'RSVP {rsvp_id}: {family_name} ({attendance}) - Event {event_id} (User {user_id}) - {bride_name} & {groom_name}')

conn.close()