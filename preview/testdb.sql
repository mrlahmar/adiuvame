-- Adminer 4.6.3-dev PostgreSQL dump

DROP TABLE IF EXISTS "comment";
DROP SEQUENCE IF EXISTS comment_comment_id_seq;
CREATE SEQUENCE comment_comment_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."comment" (
    "comment_id" integer DEFAULT nextval('comment_comment_id_seq') NOT NULL,
    "comment_content" text NOT NULL,
    "comment_timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "comment_post" integer NOT NULL,
    "comment_writer" integer NOT NULL,
    CONSTRAINT "comment_pkey" PRIMARY KEY ("comment_id"),
    CONSTRAINT "comment_comment_post_fkey" FOREIGN KEY (comment_post) REFERENCES post(post_id) ON DELETE CASCADE,
    CONSTRAINT "comment_comment_writer_fkey" FOREIGN KEY (comment_writer) REFERENCES users(user_id) ON DELETE CASCADE
) WITH (oids = false);

INSERT INTO "comment" ("comment_id", "comment_content", "comment_timestamp", "comment_post", "comment_writer") VALUES
(6,	'Hello, I''m jack, I''ve just sent u an email right now, check ur inbox, so we can plan a meeting ',	'2019-08-03 11:56:18.632389',	9,	10),
(7,	'Hi I''m Jack, I can lend my wheelchair, I''ve sent an email, check out ur inbox',	'2019-08-03 11:58:41.938829',	10,	10);

DROP TABLE IF EXISTS "post";
DROP SEQUENCE IF EXISTS post_post_id_seq;
CREATE SEQUENCE post_post_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."post" (
    "post_id" integer DEFAULT nextval('post_post_id_seq') NOT NULL,
    "post_title" text NOT NULL,
    "post_content" text NOT NULL,
    "post_timestamp" timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "post_publisher" integer NOT NULL,
    CONSTRAINT "post_pkey" PRIMARY KEY ("post_id"),
    CONSTRAINT "post_post_publisher_fkey" FOREIGN KEY (post_publisher) REFERENCES users(user_id) NOT DEFERRABLE
) WITH (oids = false);

INSERT INTO "post" ("post_id", "post_title", "post_content", "post_timestamp", "post_publisher") VALUES
(9,	'Invacare Electric Wheelchair for Donation',	'Hello I''m Ala from Tunisia

I have an Invacare Stream wheelchair, that I want to donate
it''s in a good working condition,  for more info comment or email

I''m available every day between 4PM and 6PM in case you want to take it from my garage, (Garage Address : 144 Bourguiba Street )',	'2019-08-03 11:48:01.007815',	1),
(10,	'I need a sport wheelchair',	'Hello Guys, I''m adam

I''m going to participate in a wheelchair marathon, and this is my first time to do this, and I''m asking if anyone has a sport wheelchair that I can use this week

Cheers',	'2019-08-03 11:53:23.081894',	2);

DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_user_id_seq;
CREATE SEQUENCE users_user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "user_id" integer DEFAULT nextval('users_user_id_seq') NOT NULL,
    "username" text NOT NULL,
    "fullname" text NOT NULL,
    "email" text NOT NULL,
    "password_hash" text NOT NULL,
    "phone" character varying(20) NOT NULL,
    CONSTRAINT "users_email_key" UNIQUE ("email"),
    CONSTRAINT "users_phone_key" UNIQUE ("phone"),
    CONSTRAINT "users_pkey" PRIMARY KEY ("user_id"),
    CONSTRAINT "users_username_key" UNIQUE ("username")
) WITH (oids = false);

INSERT INTO "users" ("user_id", "username", "fullname", "email", "password_hash", "phone") VALUES
(2,	'adam',	'Adam',	'adam@adam.com',	'pbkdf2:sha256:150000$DdNtyj8F$f75dc6c47e3d7db357513b7b7b457a9f9dc7ae346d98cee6127b7b2179e15b3b',	'123'),
(10,	'jack',	'Jack Thom',	'jack@thom.com',	'pbkdf2:sha256:150000$JHFraYo1$fa0fe9ac763d80dd5f954540735190da298ca9838b94aaf22bf04fb6e5a64796',	'+14586'),
(11,	'mark',	'Mark',	'mark@mark.com',	'pbkdf2:sha256:150000$ax78ANYE$5c1ea474eb2ce18f81cb4db370523901e2ae2fd525ccb8981c85382924f99015',	'+254545'),
(1,	'mrlahmar',	'Alaa Lahmar',	'ala@lahmar.com',	'pbkdf2:sha256:150000$EFr7Zs1K$4866a99a176776eac343647c9d00347e23466b65e2defe937b479cecd385152a',	'46464646');

-- 2019-08-03 13:59:36.676789+00