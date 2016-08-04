# Host: 127.0.0.1  (Version 5.6.20)
# Date: 2016-08-04 14:31:13
# Generator: MySQL-Front 5.3  (Build 7.6)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "content_rule"
#

DROP TABLE IF EXISTS `content_rule`;
CREATE TABLE `content_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `list_regex` varchar(255) DEFAULT NULL COMMENT '列表页-正则',
  `regex_or_xpath` char(1) DEFAULT '0' COMMENT '0:xpath, 1:正则',
  `item` varchar(255) NOT NULL DEFAULT 'title' COMMENT 'title，author，ctime，content 等',
  `content_rule` varchar(255) DEFAULT NULL COMMENT '匹配规则',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `item` (`item`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

#
# Structure for table "current_domain_setting"
#

DROP TABLE IF EXISTS `current_domain_setting`;
CREATE TABLE `current_domain_setting` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `start_url` varchar(255) DEFAULT NULL,
  `site_domain` varchar(255) DEFAULT NULL,
  `black_domain_str` varchar(255) DEFAULT NULL COMMENT '以 ; 分割的列表',
  `setting_json` longtext COMMENT '配置简报，json版',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8;

#
# Structure for table "result_file"
#

DROP TABLE IF EXISTS `result_file`;
CREATE TABLE `result_file` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT '',
  `start_url` varchar(255) NOT NULL DEFAULT '',
  `site_domain` varchar(255) DEFAULT '',
  `list_result_file` longblob COMMENT '结果文件（.txt）',
  `detail_result_file` longblob COMMENT '结果文件（.txt）',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `user_id` (`user_id`,`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8 COMMENT='列表页结果-文件形式';

#
# Structure for table "url_rule"
#

DROP TABLE IF EXISTS `url_rule`;
CREATE TABLE `url_rule` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT 'admin' COMMENT 'user',
  `start_url` varchar(255) NOT NULL DEFAULT '' COMMENT 'homepage',
  `site_domain` varchar(255) NOT NULL DEFAULT '' COMMENT 'domain',
  `black_domain_str` varchar(255) DEFAULT NULL COMMENT 'black_domain_str  <-  ; ; ;',
  `detail_or_list` char(1) DEFAULT '0' COMMENT '0:detail,1:list',
  `scope` char(1) NOT NULL DEFAULT '0' COMMENT '0:netloc,1:path,2:query',
  `white_or_black` char(1) NOT NULL DEFAULT '0' COMMENT '0:white,1:black',
  `weight` char(1) NOT NULL DEFAULT '0' COMMENT '0:高，1：中，2：低',
  `regex` varchar(255) DEFAULT NULL COMMENT '正则表达式',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `scope` (`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=442 DEFAULT CHARSET=utf8;

#
# Structure for table "user"
#

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `Authorization` char(1) DEFAULT NULL COMMENT '0:admin,1:normal',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
