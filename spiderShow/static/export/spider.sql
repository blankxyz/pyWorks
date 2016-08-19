﻿# Host: 127.0.0.1  (Version 5.6.20)
# Date: 2016-08-18 23:48:59
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
# Data for table "content_rule"
#

INSERT INTO `content_rule` VALUES (5,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','0','title','//tr[@valign=\"top\"]//strong',NULL),(6,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','0','author','',NULL),(7,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','0','content','//div[@id=\"ozoom\"]',NULL),(8,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','','0','ctime','//td[@align=\"middle\"]/text()',NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8;

#
# Data for table "current_domain_setting"
#


#
# Structure for table "preset_patrn"
#

DROP TABLE IF EXISTS `preset_patrn`;
CREATE TABLE `preset_patrn` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `partn_type` varchar(255) DEFAULT NULL COMMENT 'list,detail,rubbish',
  `partn` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

#
# Data for table "preset_patrn"
#

INSERT INTO `preset_patrn` VALUES (1,'rubbish','uid'),(2,'rubbish','username'),(3,'rubbish','space'),(4,'rubbish','search'),(5,'rubbish','blog'),(6,'rubbish','group'),(7,'list','list'),(8,'list','index'),(9,'list','forum'),(10,'list','fid'),(11,'detail','post'),(12,'detail','thread'),(13,'detail','detail'),(14,'detail','content');

#
# Structure for table "result_file"
#

DROP TABLE IF EXISTS `result_file`;
CREATE TABLE `result_file` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT '',
  `start_url` varchar(255) NOT NULL DEFAULT '',
  `site_domain` varchar(255) DEFAULT '',
  `advice_start_url_list` longtext,
  `advice_regex_list` longtext,
  `advice_keyword_list` longtext,
  `list_result_file` longblob COMMENT '结果文件（.txt）',
  `detail_result_file` longblob COMMENT '结果文件（.txt）',
  PRIMARY KEY (`Id`),
  KEY `user_id` (`user_id`,`start_url`,`site_domain`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8 COMMENT='列表页结果-文件形式';

#
# Data for table "result_file"
#
#
# Structure for table "task_manage"
#

DROP TABLE IF EXISTS `task_manage`;
CREATE TABLE `task_manage` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(255) NOT NULL DEFAULT 'admin',
  `start_url` varchar(255) NOT NULL DEFAULT '',
  `site_domain` varchar(255) DEFAULT NULL,
  `status` varchar(255) NOT NULL DEFAULT '''0''' COMMENT '0:准备，1:执行中，9：执行完毕',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Data for table "task_manage"
#


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
) ENGINE=InnoDB AUTO_INCREMENT=789 DEFAULT CHARSET=utf8;

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (774,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','post',NULL),(775,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','thread',NULL),(776,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','news-',NULL),(777,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','info.asp',NULL),(778,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','/\\d+.html',NULL),(779,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','info-',NULL),(780,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','shop-',NULL),(781,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','0','1','0','0','/[a-zA-Z]+/[a-zA-Z]+-\\d+.html',NULL),(782,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','0','0','list',NULL),(783,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','0','0','\\/$',NULL),(784,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','0','0','index',NULL),(785,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','0','0','forum',NULL),(786,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','0','0','/[a-zA-Z]+/[a-zA-Z]+.html',NULL),(787,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','1','0','/^login/',NULL),(788,'admin','http://www.ynsf.ccoo.cn','www.ynsf.ccoo.cn','','1','1','1','0','/^/reg//',NULL);

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

#
# Data for table "user"
#

INSERT INTO `user` VALUES (1,'admin','admin','0','admin'),(2,'user','user','1','normal user');
