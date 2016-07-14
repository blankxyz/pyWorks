# Host: 127.0.0.1  (Version: 5.6.20)
# Date: 2016-07-14 15:17:18
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
# Structure for table "setting"
#

DROP TABLE IF EXISTS `setting`;
CREATE TABLE `setting` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `start_urls` varchar(255) NOT NULL DEFAULT '',
  `site_domain` varchar(255) NOT NULL DEFAULT '',
  `setting_json` varchar(255) NOT NULL DEFAULT '' COMMENT 'json版 setting',
  `url_rule_id` int(11) NOT NULL DEFAULT '0',
  `content_rule_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `setting_start_urls_site_domain_pk` (`start_urls`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8;

#
# Data for table "setting"
#

INSERT INTO `setting` VALUES (24,'http://cpt.xtu.edu.cn/','cpt.xtu.edu.cn','{\"regex_save_list\": [\"/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[a-zA-Z]{1,}/[0-9a-zA-Z]{1,}/\\d{4}/?\\d{4}/\\d{1,}.html\"], \"site_domain\": \"cpt.xtu.edu.cn\", \"start_urls\": \"http://cpt.xtu.edu.cn/\", \"list_keys\": [\"list\", \"index\"], \"detail_keys\": [\"post\", \"content\", \"detail\"]',0,NULL),(25,'http://bbs.tianya.cn/','bbs.tianya.cn','{\"regex_save_list\": [\"/[a-zA-Z]{1,}/[a-zA-Z]{1,}/\\d{4}\\/?\\d{4}/\\d{1,}.html\"], \"site_domain\": \"bbs.tianya.cn\", \"start_urls\": \"http://bbs.tianya.cn/\", \"list_keys\": [\"list\", \"index\"], \"detail_keys\": [\"post\", \"content\", \"detail\"]}',0,NULL);

#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `scope` int(2) DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `yes_no` bit(1) DEFAULT b'0' COMMENT '0:white,1:black',
  `weight` int(2) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  `update_time` datetime NOT NULL DEFAULT '0000-00-00 00:00:00' COMMENT '更新（做成）时间',
  PRIMARY KEY (`Id`),
  KEY `scope` (`scope`,`yes_no`,`weight`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='url匹配规则';

#
# Data for table "url_rule"
#

