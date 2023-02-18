DROP TABLE IF EXISTS `metadata`;

create table metadata
(
    measurement     varchar(18)  not null
        primary key,
    location        text,
    distance        float(20, 2) not null,
    username        text,
    measurementname text,
    notes text
);



CREATE TABLE IF NOT EXISTS `ExampleTable` (
  `IDX` int(8) NOT NULL,
  `POSITION` float(10,2) DEFAULT NULL,
  `HOEHE` float(5,2) NOT NULL,
  `GESCHWINDIGKEIT` float(5,2) DEFAULT NULL,
  `BREITE` int(4) DEFAULT NULL,
  `GRENZWERT` int(4) DEFAULT NULL
);

CREATE TABLE `comments` (
  `measurement` varchar(20) NOT NULL,
  `position` float(10,2) NOT NULL,
  `comment` varchar(30) NOT NULL,
  PRIMARY KEY (`measurement`,`position`)
);

CREATE TABLE `commentBtns` (
  `comment` varchar(30) DEFAULT NULL
);