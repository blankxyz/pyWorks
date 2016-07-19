# Host: 127.0.0.1  (Version: 5.6.20)
# Date: 2016-07-19 17:47:37
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
# Structure for table "current_domain_setting"
#

DROP TABLE IF EXISTS `current_domain_setting`;
CREATE TABLE `current_domain_setting` (
  `Id` int(11) NOT NULL DEFAULT '0',
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `black_domain` varchar(255) DEFAULT NULL COMMENT '以 ; 分割的列表',
  `setting_json` longtext COMMENT '配置简报，json版',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='初始化配置，只有一条当前配置记录。';

#
# Data for table "current_domain_setting"
#

INSERT INTO `current_domain_setting` VALUES (0,'http://bbs.tianya.cn','bbs.tianya.cn','blog.tianya.cn','{\"detail_regex_save_list\": [[\"thread\", \"100\"], [\"post-\", \"100\"], [\"pic-\", \"100\"]], \"site_domain\": \"bbs.tianya.cn\", \"list_regex_save_list\": [[\"\\/$\", \"100\"], [\"list\", \"100\"], [\"index\", \"100\"]], \"start_url\": \"http://bbs.tianya.cn\"}');

#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `start_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'homepage',
  `site_domain` varchar(255) NOT NULL DEFAULT '' COMMENT 'domain',
  `detail_or_list` char(1) DEFAULT '0' COMMENT '0:detail,1:list',
  `scope` char(1) NOT NULL DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `white_or_black` char(1) NOT NULL DEFAULT '0' COMMENT '0:white,1:black',
  `weight` char(1) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `scope` (`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=94 DEFAULT CHARSET=utf8 COMMENT='url匹配规则';

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (182,'http://bbs.tianya.cn','bbs.tianya.cn','0','1','0','1','thread',NULL),(183,'http://bbs.tianya.cn','bbs.tianya.cn','0','1','0','1','post-',NULL),(184,'http://bbs.tianya.cn','bbs.tianya.cn','0','1','0','1','pic-',NULL),(185,'http://bbs.tianya.cn','bbs.tianya.cn','1','1','0','1','/$',NULL),(186,'http://bbs.tianya.cn','bbs.tianya.cn','1','1','0','1','list',NULL),(187,'http://bbs.tianya.cn','bbs.tianya.cn','1','1','0','1','index',NULL);
