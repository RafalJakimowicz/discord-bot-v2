--create table for notes [0]
CREATE TABLE IF NOT EXISTS notes(
    id SERIAL PRIMARY KEY,
    note_id BIGINT UNIQUE,
    author_id BIGINT,
    title TEXT,
    content TEXT,
    creation_date TEXT
);

--create table for notes members [1]
CREATE TABLE IF NOT EXISTS notes_users(
    id SERIAL PRIMARY KEY,
    member_id BIGINT,
    note_id BIGINT NOT NULL,
    CONSTRAINT fk_notes
        FOREIGN KEY (note_id)
            REFERENCES notes(note_id)
            ON DELETE CASCADE
);

--add note [2]
INSERT INTO notes (
    note_id, 
    author_id, 
    title, 
    content, 
    creation_date
)
VALUES (%s,%s,%s,%s,%s);

--add note member [3]
INSERT INTO notes_users (
    member_id,
    note_id
)
VALUES (%s,%s);

--get note by id [4]
SELECT * FROM notes WHERE note_id = %s;

--get note id by user id [5]
SELECT * FROM notes_users WHERE member_id = %s;

--get note users by note id [6]
SELECT * FROM notes WHERE note_id = %s;