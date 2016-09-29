# Host: 127.0.0.1  (Version 5.6.20)
# Date: 2016-09-29 22:10:07
# Generator: MySQL-Front 5.4  (Build 1.1)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "yt_comments"
#

DROP TABLE IF EXISTS `yt_comments`;
CREATE TABLE `yt_comments` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(255) DEFAULT NULL,
  `video_id` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `text` varchar(255) DEFAULT NULL,
  `updated` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Data for table "yt_comments"
#


#
# Structure for table "yt_keywords"
#

DROP TABLE IF EXISTS `yt_keywords`;
CREATE TABLE `yt_keywords` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Data for table "yt_keywords"
#

INSERT INTO `yt_keywords` VALUES (1,'china');
