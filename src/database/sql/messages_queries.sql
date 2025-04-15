--init messages table [0]
CREATE TABLE IF NOT EXISTS messages
(
    id SERIAL PRIMARY KEY,
    message_id BIGINT UNIQUE,
    user_id BIGINT,
    timestamp TEXT,
    guild_name TEXT,
    channel_name TEXT,
    content TEXT
);

--init deleted messages query [1]
CREATE TABLE IF NOT EXISTS deleted_messages
(
    id SERIAL PRIMARY KEY,
    message_id BIGINT UNIQUE NOT NULL,
    CONSTRAINT fk_message
        FOREIGN KEY (message_id)
            REFERENCES messages(message_id)
            ON DELETE CASCADE
);

--edited messages query [2]
CREATE TABLE IF NOT EXISTS edited_messages
(
    id SERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    before_content TEXT,
    after_content TEXT,
    CONSTRAINT fk_message
        FOREIGN KEY (message_id)
            REFERENCES messages(message_id)
            ON DELETE CASCADE
);

--get message by id [3]
SELECT * FROM messages WHERE message_id = %s;

--add deleted message [4]
INSERT INTO deleted_messages (message_id)
VALUES (%s); 

--add edited message [5]
INSERT INTO edited_messages (message_id, before_content, after_content)
VALUES (%s, %s, %s);

--add message [6]
INSERT INTO messages (message_id, user_id, timestamp, guild_name, channel_name, content)
VALUES (%s,%s,%s,%s,%s,%s);

--get all messages [7]
SELECT * FROM messages;

--get members messages by username [8]
SELECT u.username AS member_username, m.*
FROM members AS u
INNER JOIN messages AS m
    ON m.user_id = u.user_id
    WHERE u.username = %s;