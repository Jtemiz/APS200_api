DROP TABLE IF EXISTS `metadata`;

CREATE TABLE `metadata` (
  `measurement` varchar(18) NOT NULL,
  `place` varchar(30) DEFAULT NULL,
  `distance` float(10,2) DEFAULT NULL,
  `user` varchar(30) DEFAULT NULL,
  `measure` varchar(100) DEFAULT 'Nicht angegeben',
  `date` datetime NOT NULL,
  PRIMARY KEY (`measurement`)
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