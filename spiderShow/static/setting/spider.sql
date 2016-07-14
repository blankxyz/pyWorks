# Host: 127.0.0.1  (Version: 5.6.20)
# Date: 2016-07-14 17:04:55
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
  `update_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '更新（做成）时间',
  PRIMARY KEY (`Id`),
  KEY `item` (`item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='提取内容的规则（xpath）';

#
# Data for table "content_rule"
#


#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `start_urls` varchar(255) NOT NULL DEFAULT '' COMMENT 'homepage',
  `site_domain` varchar(255) NOT NULL DEFAULT '' COMMENT 'domain',
  `scope` int(1) NOT NULL DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `yes_no` bit(1) NOT NULL DEFAULT b'0' COMMENT '0:white,1:black',
  `weight` int(1) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  `setting_json` longtext NOT NULL COMMENT 'json版 setting',
  `update_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '更新（做成）时间',
  PRIMARY KEY (`Id`),
  KEY `scope` (`start_urls`,`site_domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='url匹配规则';

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (1,'http://bbs.tianya.cn/','bbs.tianya.cn',0,b'0',0,'index',NULL,'{\'index\':index}','0000-00-00 00:00:00');
