# -*- coding: utf-8 -*-
import sqlite3
conn = sqlite3.connect('app.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE users ADD COLUMN display_name VARCHAR')
except sqlite3.OperationalError:
    pass
c.execute("UPDATE users SET display_name='Administrator' WHERE username='admin'")
c.execute("UPDATE users SET display_name='Nguyên' WHERE username='nguyen'")
c.execute("UPDATE users SET display_name=username WHERE display_name IS NULL")
conn.commit()
conn.close()
print('DB Updated')
