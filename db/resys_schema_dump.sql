PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    useraccount text,
    firstname text, 
    lastname text,
    email text, 
    mobile text,
    active integer,
    UNIQUE(useraccount, email));

/*CREATE TABLE IF NOT EXISTS admins(
    user_id integer,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_id) REFERENCES users(use_id));
*/

CREATE TABLE IF NOT EXISTS items(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    status INTEGER,
    description TEXT);

CREATE TABLE IF NOT EXISTS reservations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item INTEGER,
    user INTEGER,
    ldate INTEGER,
    rdate INTEGER,
    FOREIGN KEY(user) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(item) REFERENCES items(id) ON DELETE CASCADE);

COMMIT;
PRAGMA foreign_keys=ON;
