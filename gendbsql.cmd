sqlite3 instance/hzlinkdb.db "select 'DROP TRIGGER '||name||';' from sqlite_master where type = 'trigger'" > database.sql
sqldiff instance/hzlinkdb.db.old instance/hzlinkdb.db >> database.sql
sqlite3 instance/hzlinkdb.db "select sql||';' from sqlite_master where type = 'trigger'" >> database.sql
