CREATE TABLE article
(
    id INT(11) PRIMARY KEY NOT NULL,
    title VARCHAR(45),
    content VARCHAR(45),
    image LONGBLOB,
    create_at DATETIME
);
CREATE TABLE comment
(
    id INT(11) PRIMARY KEY NOT NULL,
    comment VARCHAR(45),
    create_at DATETIME,
    article_id INT(11),
    user_name VARCHAR(45)
);

INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (1, 'title1', 'content1', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (2, 'title2', 'content2', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (3, 'title3', 'content3', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (4, 'title4', 'content4', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (5, 'title5', 'content5', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (6, 'title6', 'content6', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (7, 'title7', 'content7', '/static/2.png', '2017-01-16 21:10:13');
INSERT INTO facePlus.article (id, title, content, image, create_at) VALUES (8, 'title8', 'content8', '/static/2.png', '2017-01-16 21:10:13');


INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (1, 'user1', 'user1 comment1', '2017-01-16 21:09:23', 1);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (2, 'user2', 'user2 comment1', '2017-01-16 21:09:23', 1);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (3, 'user1', 'user1 comment1', '2017-01-16 21:09:23', 2);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (4, 'user2', 'user2 comment1', '2017-01-16 21:09:23', 2);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (5, 'user1', 'user1 comment2', '2017-01-16 21:09:23', 2);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (6, 'user2', 'user2 comment2', '2017-01-16 21:09:23', 2);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (7, 'user3', 'user3 comment1', '2017-01-16 21:09:23', 3);
INSERT INTO facePlus.comment (id, user_name, comment, create_at, article_id) VALUES (8, 'user3', 'user3 comment2', '2017-01-16 21:09:23', 3);