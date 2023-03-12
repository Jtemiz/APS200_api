create database aps200;
create user 'aps200'@'%' identified by 'Jockel01.';
grant all privileges on *.* to 'aps200'@'%';
flush privileges;

create table if not exists ExampleTable
(
    POSITION        float(11, 3) null,
    HOEHE           float(6, 3)  not null,
    GESCHWINDIGKEIT float(6, 3)  null,
    BREITE          int          null,
    GRENZWERT       int          null
);

create table if not exists commentBtns
(
    comment varchar(10000) null
);

create table if not exists comments
(
    measurement varchar(20)    not null,
    position    float(10, 2)   not null,
    comment     varchar(10000) not null,
    primary key (measurement, position)
);

create table if not exists metadata
(
    measurement     varchar(18)  not null
        primary key,
    location        text         null,
    distance        float(20, 2) not null,
    username        text         null,
    measurementname text         null,
    notes           text         null
);


