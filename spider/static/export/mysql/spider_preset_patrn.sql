-- MySQL dump 10.13  Distrib 5.7.12, for osx10.9 (x86_64)
--
-- Host: localhost    Database: spider
-- ------------------------------------------------------
-- Server version	5.7.13

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `preset_patrn`
--

DROP TABLE IF EXISTS `preset_patrn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `preset_patrn` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `scope` varchar(255) DEFAULT '''01''' COMMENT '01新闻、02论坛、03博客、04微博 05平媒 06微信  07 视频、99搜索引擎',
  `partn_type` varchar(255) DEFAULT NULL COMMENT 'list,detail,rubbish',
  `partn` varchar(255) DEFAULT NULL,
  `weight` varchar(255) DEFAULT '0' COMMENT '0：确定, 1：可能, 2： 。。。',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preset_patrn`
--

LOCK TABLES `preset_patrn` WRITE;
/*!40000 ALTER TABLE `preset_patrn` DISABLE KEYS */;
INSERT INTO `preset_patrn` VALUES (52,'01','rubbish','uid','1'),(53,'01','rubbish','username','1'),(54,'01','rubbish','space','1'),(55,'01','rubbish','search','1'),(56,'01','rubbish','blog','1'),(57,'01','rubbish','group','1'),(58,'01','list','list','1'),(59,'01','list','index','1'),(60,'01','list','forum','1'),(61,'01','list','fid','1'),(62,'01','detail','post','1'),(63,'01','detail','thread','1'),(64,'01','detail','detail','1'),(65,'01','detail','content','1'),(66,'02','list','/list-','1'),(67,'02','list','/hotArticle','1'),(68,'02','detail','/post-','1'),(69,'02','list','\\/$','1');
/*!40000 ALTER TABLE `preset_patrn` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-08-28 22:41:27
