# Host: 127.0.0.1  (Version: 5.6.20)
# Date: 2016-07-15 22:09:05
# Generator: MySQL-Front 5.3  (Build 4.214)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "content_rule"
#

DROP TABLE IF EXISTS `content_rule`;
CREATE TABLE `content_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `item` varchar(255) NOT NULL DEFAULT 'title' COMMENT 'title，ctime，gtime，content 等',
  `rule` varchar(255) DEFAULT NULL COMMENT '匹配规则',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `item` (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='提取内容的规则（xpath）';

#
# Data for table "content_rule"
#


#
# Structure for table "current_main_setting"
#

DROP TABLE IF EXISTS `current_main_setting`;
CREATE TABLE `current_main_setting` (
  `Id` int(11) NOT NULL DEFAULT '0',
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `setting_json` longtext COMMENT '配置简报，json版',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='初始化配置，只有一条当前配置记录。';

#
# Data for table "current_main_setting"
#


#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `start_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'homepage',
  `site_domain` varchar(255) NOT NULL DEFAULT '' COMMENT 'domain',
  `black_domain` varchar(255) DEFAULT NULL,
  `detail_or_list` char(1) DEFAULT '0' COMMENT '0:detail,1:list',
  `scope` char(1) NOT NULL DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `white_or_black` char(1) NOT NULL DEFAULT '0' COMMENT '0:white,1:black',
  `weight` char(1) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `scope` (`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8 COMMENT='url匹配规则';

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (26,'http://bbs.tianya.cn','bbs.tianya.cn',NULL,'0','1','0','1','detail1',NULL),(27,'http://bbs.tianya.cn','bbs.tianya.cn',NULL,'0','1','0','1','detail2',NULL),(28,'http://bbs.tianya.cn','bbs.tianya.cn',NULL,'1','1','0','1','/[a-zA-Z]{1}/[a-zA-Z]{7}/d{4}/d{4}/d{3}.html',NULL),(29,'http://bbs.tianya.cn','bbs.tianya.cn',NULL,'1','1','0','1','list1',NULL);
