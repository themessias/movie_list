drop table if exists users;

drop table if exists movies;

create table users(email varchar(100) primary key,
            password varchar(512) not null);

create table movies(id serial primary key,
            title varchar(50) not null,
            user_email varchar(100) not null,
            year smallint,
            link varchar(200));