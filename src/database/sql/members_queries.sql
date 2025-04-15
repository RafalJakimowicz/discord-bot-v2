--members table init [0]
CREATE TABLE IF NOT EXISTS members
(
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    username TEXT
);

--member join and leaves [1]
CREATE TABLE IF NOT EXISTS member_joins_leaves
(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    time_stamp TEXT,
    is_join BOOL,
    is_leave BOOL,
    CONSTRAINT fk_members
        FOREIGN KEY (user_id)
            REFERENCES members(user_id)
            ON DELETE CASCADE
);

--get member by id [2]
SELECT * FROM member WHERE user_id = %s;

--add member [3]
INSERT INTO members (user_id, username)
VALUES (%s, %s)
ON CONFLICT (user_id) 
    DO UPDATE SET
    username = EXCLUDED.username;

--trac member statuses [4]
INSER INTO member_joins_leaves (user_id, time_stamp, is_join, is_leave) 
VALUES (%s, %s, %s, %s);

--update member username [5]
UPDATE members SET username = %s WHERE user_id = %s;

--get all statuses [6]
SELECT * FROM member_joins_leaves;

--get all members [7]
SELECT * FROM members;