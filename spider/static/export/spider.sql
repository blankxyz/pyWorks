# Host: 127.0.0.1  (Version 5.6.20)
# Date: 2016-09-08 22:58:09
# Generator: MySQL-Front 5.4  (Build 1.1)

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
  `info_flg` varchar(255) DEFAULT NULL COMMENT '01新闻、02论坛、03博客、04微博 05平媒 06微信 07 视频、99搜索引擎',
  `list_regex` varchar(255) DEFAULT NULL COMMENT '列表页-正则',
  `regex_or_xpath` char(1) DEFAULT '0' COMMENT '0:xpath, 1:正则',
  `item` varchar(255) NOT NULL DEFAULT 'title' COMMENT 'title，author，ctime，content 等',
  `content_rule` varchar(255) DEFAULT NULL COMMENT '匹配规则',
  `etc` varchar(255) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`Id`),
  KEY `item` (`item`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8;

#
# Data for table "content_rule"
#

INSERT INTO `content_rule` VALUES (5,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','01','','0','title','//tr[@valign=\"top\"]//strong',NULL),(6,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','01','','0','author','',NULL),(7,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','01','','0','content','//div[@id=\"ozoom\"]',NULL),(8,'admin','http://bbs.hefei.cc/','bbs.hefei.cc','01','','0','ctime','//td[@align=\"middle\"]/text()',NULL),(77,'admin','http://bbs.tianya.cn','bbs.tianya.cn','01','','0','title','.//*[@id=\'post_head\']/h1/span[1]/span',NULL),(78,'admin','http://bbs.tianya.cn','bbs.tianya.cn','01','','0','author','//*[@id=\'bd\']/div[4]/div[1]/div/div[2]/div[1]',NULL),(79,'admin','http://bbs.tianya.cn','bbs.tianya.cn','01','','0','content','//*[@id=\'bd\']/div[4]/div[1]/div/div[2]/div[1]',NULL),(80,'admin','http://bbs.tianya.cn','bbs.tianya.cn','01','','0','ctime','.//*[@id=\'bd\']/div[4]/div[1]/div/div[2]/div[1]',NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=412 DEFAULT CHARSET=utf8;

#
# Data for table "current_domain_setting"
#

INSERT INTO `current_domain_setting` VALUES (190,'user','http://bbs.tianya.cn','bbs.tianya.cn','',''),(411,'admin','http://www.ynsf.ccoo.cn','ynsf.ccoo.cn','','');

#
# Structure for table "preset_patrn"
#

DROP TABLE IF EXISTS `preset_patrn`;
CREATE TABLE `preset_patrn` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `info_flg` varchar(255) DEFAULT '''01''' COMMENT '01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎',
  `partn_type` varchar(255) DEFAULT NULL COMMENT 'list,detail,rubbish',
  `partn` varchar(255) DEFAULT NULL,
  `weight` varchar(255) DEFAULT '0' COMMENT '0：确定, 1：可能, 2： 。。。',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=134 DEFAULT CHARSET=utf8;

#
# Data for table "preset_patrn"
#

INSERT INTO `preset_patrn` VALUES (66,'02','list','/list-','1'),(67,'02','list','/hotArticle','1'),(68,'02','detail','/post-','1'),(69,'02','list','\\/$','1'),(101,'03','list','/list1','0'),(102,'01','rubbish','uid','1'),(103,'01','rubbish','username','1'),(104,'01','rubbish','space','1'),(105,'01','rubbish','search','1'),(106,'01','rubbish','blog','1'),(107,'01','rubbish','group','1'),(108,'01','list','list','1'),(109,'01','list','index','1'),(110,'01','list','forum','1'),(111,'01','list','fid','1'),(112,'01','detail','post','1'),(113,'01','detail','thread','1'),(114,'01','detail','detail','1'),(115,'01','detail','content','1'),(131,'06','list','bbb','0'),(132,'02','detail','thread','1'),(133,'02','list','forum','1');

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
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8 COMMENT='列表页结果-文件形式';

#
# Data for table "result_file"
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
) ENGINE=InnoDB AUTO_INCREMENT=1430 DEFAULT CHARSET=utf8;

#
# Data for table "url_rule"
#

INSERT INTO `url_rule` VALUES (1015,'user','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','/post-',NULL),(1016,'user','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','/list-',NULL),(1017,'user','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','/hotArticle',NULL),(1018,'user','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','1','0','/^space/',NULL),(1019,'user','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','1','0','/^search/',NULL),(1072,'admin','http://www.qbjggzy.com','qbjggzy.com','','0','1','0','0','/Article/ArticleDetail',NULL),(1073,'admin','http://www.qbjggzy.com','qbjggzy.com','','1','1','0','0','/',NULL),(1074,'admin','http://www.qbjggzy.com','qbjggzy.com','','1','1','0','0','Category',NULL),(1101,'admin','http://liuyan.people.com.cn/index.php?gid=4','liuyan.people.com.cn','','0','1','0','0','/post.php',NULL),(1102,'admin','http://liuyan.people.com.cn/index.php?gid=4','liuyan.people.com.cn','','1','1','0','0','/index.php',NULL),(1103,'admin','http://liuyan.people.com.cn/index.php?gid=4','liuyan.people.com.cn','','1','1','0','0','/city.php',NULL),(1104,'admin','http://liuyan.people.com.cn/index.php?gid=4','liuyan.people.com.cn','','1','1','0','0','\\/$',NULL),(1105,'admin','http://liuyan.people.com.cn/index.php?gid=4','liuyan.people.com.cn','','1','1','0','0','/list.php',NULL),(1106,'admin','http://liuyan.people.com.cn/city.php?fid=638','liuyan.people.com.cn','','1','1','0','0','/index.php',NULL),(1409,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','/post-',NULL),(1410,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','0','1','0','0','aaa',NULL),(1411,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','/list-',NULL),(1412,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','1','/hotArticle',NULL),(1413,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','1','\\/$',NULL),(1414,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','/list.jsp',NULL),(1415,'admin','http://bbs.tianya.cn','bbs.tianya.cn','','1','1','0','0','aa',NULL),(1416,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','0','1','0','1','/post-',NULL),(1417,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','0','1','0','1','thread',NULL),(1418,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','1','1','0','1','/list-',NULL),(1419,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','1','1','0','1','/hotArticle',NULL),(1420,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','1','1','0','1','\\/$',NULL),(1421,'admin','http://bbs.shunderen.com','bbs.shunderen.com','','1','1','0','1','forum',NULL),(1429,'admin','http://www.ynsf.ccoo.cn','ynsf.ccoo.cn','','1','1','0','0','\\/$',NULL);

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
