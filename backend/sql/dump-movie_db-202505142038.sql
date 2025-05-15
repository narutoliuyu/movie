-- MySQL dump 10.13  Distrib 5.7.26, for Win64 (x86_64)
--
-- Host: localhost    Database: movie_db
-- ------------------------------------------------------
-- Server version	5.7.26

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
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('ecc7e6c5efa6');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categories` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'动作','动作类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(2,'喜剧','喜剧类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(3,'科幻','科幻类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(4,'爱情','爱情类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(5,'动漫','动漫类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(6,'剧情','剧情类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(7,'历史','历史类电影','2025-05-14 12:04:14','2025-05-14 12:04:14'),(8,'短视频','短视频内容','2025-05-14 12:04:14','2025-05-14 12:04:14'),(9,'VIP专区','VIP专属内容','2025-05-14 12:04:14','2025-05-14 12:04:14'),(10,'热门','热门内容','2025-05-14 12:04:14','2025-05-14 12:04:14'),(11,'消息','消息通知','2025-05-14 12:04:14','2025-05-14 12:04:14');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `category`
--

DROP TABLE IF EXISTS `category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=31 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `category`
--

LOCK TABLES `category` WRITE;
/*!40000 ALTER TABLE `category` DISABLE KEYS */;
INSERT INTO `category` VALUES (1,'动漫',NULL),(2,'剧情 ',NULL),(3,'动作',NULL),(4,'喜剧 ',NULL),(5,'动画 ',NULL),(6,'科幻',NULL),(7,'短视频',NULL),(8,'VIP',NULL),(9,'爱情 ',NULL),(10,'自然',NULL);
/*!40000 ALTER TABLE `category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie`
--

DROP TABLE IF EXISTS `movie`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movie` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `description` text COLLATE utf8_unicode_ci,
  `release_date` date DEFAULT NULL,
  `movie_type` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  `poster_url` text COLLATE utf8_unicode_ci,
  `trailer_url` text COLLATE utf8_unicode_ci,
  `director` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=49 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie`
--

LOCK TABLES `movie` WRITE;
/*!40000 ALTER TABLE `movie` DISABLE KEYS */;
INSERT INTO `movie` VALUES (25,'流浪地球2','太阳即将毁灭，人类在地球表面建造出巨大的推进器，寻找新家园。然而宇宙之路危机四伏，为了拯救地球，流浪地球时代的年轻人再次挺身而出，展开争分夺秒的生死之战。','2025-05-12','科幻','https://ts1.tc.mm.bing.net/th/id/R-C.56879a0369ddbd5ca1e1d5fdb0ee8a6a?rik=07oIiNiS4VV5wA&riu=http%3a%2f%2fn.sinaimg.cn%2fsinakd20230114ac%2f600%2fw1920h1080%2f20230114%2fdd1d-96b22f33ac81d683f28edafd06d17aa5.jpg&ehk=jFCpoBIaOx%2bHW1nF0dsXtnAf9Dtsl28%2fdadUtzUjsBU%3d&risl=&pid=ImgRaw&r=0',NULL,'郭帆',9.2,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(26,'满江红','南宋绍兴年间，岳飞死后四年，秦桧率兵与金国会谈。会谈前夜，金国使者死在宰相驻地，所携密信也不翼而飞。一个小兵与亲兵营副统领机缘巧合被裹挟进这巨大阴谋之中。','2025-05-12','科幻','https://n.sinaimg.cn/sinakd20110/69/w2000h1269/20230116/c644-326c42b1549ac186e4d22feb4de6b40b.jpg',NULL,'张艺谋',8.8,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(27,'长津湖','以抗美援朝战争第二次战役中的长津湖战役为背景，讲述了一段波澜壮阔的历史：71年前，中国人民志愿军赴朝作战，在极寒严酷环境下，东线作战部队凭着钢铁意志和英勇无畏的战斗精神一路追击，奋勇杀敌。','2025-05-12','动作','https://ts1.tc.mm.bing.net/th/id/R-C.479cd773c29a5df7a84341c73c7de88f?rik=cGGSG0bzfJjcAA&riu=http%3a%2f%2fn.sinaimg.cn%2fsinakd10011%2f550%2fw810h540%2f20210712%2f9f20-251cbf047f7f7925022892fed6310f0c.jpg&ehk=nH6fqq3CUG80nW3oGcDLXvcTl7JiP9RIKEuZvGkz6KU%3d&risl=&pid=ImgRaw&r=0',NULL,'陈凯歌',9.1,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(28,'你好，李焕英','2001年的某一天，刚刚考上大学的贾晓玲经历了人生中的一次大起大落。一心想要成为母亲骄傲的她却因母亲突遭严重意外，而悲痛万分。在贾晓玲情绪崩溃的状态下，竟意外的回到了1981年，并与年轻的母亲李焕英相遇。','2025-05-12','喜剧','https://x0.ifengimg.com/ucms/2021_07/6980130F430E92EDA8A79D215047A38E82ED076E_size1139_w1500_h1000.jpg',NULL,'贾玲',8.9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(29,'哪吒之魔童降世','天地灵气孕育出一颗能量巨大的混元珠，元始天尊将混元珠提炼成灵珠和魔丸，灵珠投胎为人，助周伐纣时可堪大用；而魔丸则会诞出魔王，为祸人间。元始天尊启动了天劫咒语，3年后天雷将会降临，摧毁魔丸。','2025-05-12','动画','https://ts1.tc.mm.bing.net/th/id/R-C.38b07fce7129e6fea619aff29e652f1a?rik=mOuOH7W9S%2b%2b3%2fQ&riu=http%3a%2f%2fwenhui.whb.cn%2fu%2fcms%2fwww%2f201907%2f26105207y1o3.jpg&ehk=yCWTJidWZdY0vbrHAdIh%2fAzHfVJm7eGd1QSu0RvsPRY%3d&risl=&pid=ImgRaw&r=0',NULL,'饺子',9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(30,'战狼2','故事发生在非洲附近的大海上，主人公冷锋遭遇人生滑铁卢，被\"开除军籍\"，本想漂泊一生的他，正当他打算这么做的时候，一场突如其来的意外打破了他的计划，突然被卷入了一场非洲国家叛乱。','2025-05-12','科幻','https://tse1-mm.cn.bing.net/th/id/OIP-C.zomD3r8U7QEpvIHi00CLygHaLV?rs=1&pid=ImgDetMain',NULL,'吴京',9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(31,'红海行动','索马里海域外，中国商船遭遇劫持，船员全数沦为阶下囚。蛟龙突击队沉着应对，潜入商船进行突袭，成功解救全部人质。返航途中，非洲北部伊维亚共和国发生政变，恐怖组织连同叛军攻入首都。','2025-05-12','动作','https://puui.qpic.cn/vcover_vt_pic/0/7casb7nes159mrl1566892576/0',NULL,'林超贤',8.9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(32,'我不是药神','普通中年男子程勇经营着一家保健品店，失意又失婚。不速之客吕受益的到来，让他开辟了一条去印度买药做\"代购\"的新事业，虽然困难重重，但他在这条\"买药之路\"上发现了商机，一发不可收拾地做起了治疗慢粒白血病的印度仿制药独家代理商。','2025-05-12','剧情','https://ts1.tc.mm.bing.net/th/id/R-C.61225195e9d5216ffa50db74754f0467?rik=GP6%2bJ25E0XArTw&riu=http%3a%2f%2fn.sinaimg.cn%2fsinacn10%2f250%2fw1750h2500%2f20180716%2f1fbd-hfkffak3865890.jpg&ehk=Z8Q2oDDxGUPOUNeGXPc9TAMMaOX%2bvQdGunw%2b3vqPrVo%3d&risl=&pid=ImgRaw&r=0',NULL,'文牧野',9.2,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(33,'唐人街探案3','继曼谷、纽约之后，东京再出大案。唐人街神探唐仁、秦风受侦探野田昊的邀请前往破案。\"CRIMASTER世界侦探排行榜\"中的侦探们闻讯后也齐聚东京，加入挑战，而排名第一Q的现身，让这个大案更加扑朔迷离。','2025-05-12','喜剧','https://tse1-mm.cn.bing.net/th/id/OIP-C.TPFt3IOtrNwezVHL98LzxAHaKX?rs=1&pid=ImgDetMain',NULL,'陈思诚',8.5,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(34,'我和我的祖国','七位导演分别取材新中国成立70周年以来，祖国经历的无数个历史性经典瞬间。讲述普通人与国家之间息息相关密不可分的动人故事。聚焦大时代大事件下，小人物和国家之间，看似遥远实则密切的关联。','2025-05-12','剧情','https://picd.zhimg.com/v2-7c54b5fb559d0c51d406de9e82404b51_720w.jpg?source=172ae18b',NULL,'陈凯歌',8.9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(35,'独行月球','人类为抵御小行星的撞击，拯救地球，在月球部署了月盾计划。陨石提前来袭，全员紧急撤离时，维修工独孤月因为意外，错过了领队马蓝星的撤离通知，一个人落在了月球。不料月盾计划失败，独孤月成为了\"宇宙最后的人类\"。','2025-05-12','科幻','https://tse1-mm.cn.bing.net/th/id/OIP-C.W5ckxt54i4FT0_iWD9rw2AHaKY?rs=1&pid=ImgDetMain',NULL,'张吃鱼',8.8,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(36,'这个杀手不太冷静','毕生追求男主梦的魏成功终于得到了女明星米兰的\"赏识\"，被邀请出演她的男一号\"杀手卡尔\"，他兴致勃勃诠释角色的同时，却没想到已经落入了一场危机四伏的阴谋。','2025-05-12','短视频','https://tse4-mm.cn.bing.net/th/id/OIP-C.fgzH6WDuub0EIow-GJ53mwHaL0?rs=1&pid=ImgDetMain',NULL,'邢文雄',8.5,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(37,'人生大事','殡葬师莫三妹在刑满释放不久后的一次出殡中，遇到了孤儿武小文，小文的出现，意外地改变了莫三妹对职业和生活的态度。','2025-05-12','VIP','https://ts1.tc.mm.bing.net/th/id/R-C.610b5b3126072a8e89385e0ab5511474?rik=ZUuUKsB16%2fujJQ&riu=http%3a%2f%2fn.sinaimg.cn%2fsinakd20220626ac%2f192%2fw1080h1512%2f20220626%2f1b85-1f8c99d45b1bd81b85dc80d82dff93a9.jpg&ehk=jtpYFz1mgga1KOzW22fEy8W7F7tfjrXDZ6iW5Ay6M38%3d&risl=&pid=ImgRaw&r=0',NULL,'刘江江',8.7,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(38,'奇迹·笨小孩','二十岁的景浩独自带着年幼的妹妹来到深圳生活，兄妹俩生活温馨却拮据。为了妹妹高昂的手术费，机缘巧合之下，景浩得到一个机会，本以为美好生活即将来临，却不料遭遇重创。','2025-05-12','VIP','https://tse2-mm.cn.bing.net/th/id/OIP-C.Bv25jtLNnY-vpTQNScqicgHaKl?rs=1&pid=ImgDetMain',NULL,'文牧野',8.9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(39,'悬崖之上','上世纪三十年代，四位曾在苏联接受特训的共产党特工组成任务小队，回国执行代号为\"乌特拉\"的秘密行动。由于叛徒的出卖，他们从跳伞降落的第一刻起，就已置身于敌人布下的罗网之中。','2025-05-12','动作','https://ts1.tc.mm.bing.net/th/id/R-C.eff4a1e3777c97a8bb3a7c8bba4ced90?rik=VsGcUBHV24HKpg&riu=http%3a%2f%2fn.sinaimg.cn%2fsinakd10108%2f79%2fw679h1000%2f20200805%2f9d7c-ixkvvuc0560941.jpg&ehk=S2LA0YTNJnkCeeAbibsrRZ6chtZFvcvWVIETGLZe8rE%3d&risl=&pid=ImgRaw&r=0',NULL,'张艺谋',9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(40,'刺杀小说家','异世界皇都，天神赤发鬼残暴统治，滥杀无辜。少年空文因被赤发鬼追杀，决定奋起反击。在黑甲的指引下，踏上了凡人弑神之路。','2025-05-12','剧情','https://ts1.tc.mm.bing.net/th/id/R-C.e4f7b45b4910f868c037cc0cb6ba81a6?rik=f3MGh3d93J5KCQ&riu=http%3a%2f%2fwww.huacemedia.com%2fupload%2fat%2fimage%2f20201222%2f1608622862523510OBnx.jpg&ehk=RZeyEnswG%2fdAFyAbAFqc5LhLhPx41tRpcKOsLLqmNuM%3d&risl=&pid=ImgRaw&r=0',NULL,'路阳',8.6,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(41,'你的婚礼','高中时，游泳特长生周潇齐对转校生尤咏慈一见钟情，年少懵懂的纯纯爱恋，男孩默默守护，但女孩却不告而别。此后的人生，15年的爱情长跑。','2025-05-12','爱情','https://ts1.tc.mm.bing.net/th/id/R-C.7dcd93f1998f0acd53ea36958fc983fa?rik=9seMgU74G1tAKg&riu=http%3a%2f%2fimg.ewang.com%2fe348af7209e89be3abef.jpg&ehk=l94RGQ63vO8jiGY7QjihaxsXkmai2bOBmofMsfSNy4k%3d&risl=&pid=ImgRaw&r=0',NULL,'韩天',8.3,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(42,'我要我们在一起','十年前，差生吕钦扬当众告白凌一尧，两人从校园步入社会，为了让她幸福，他不惜以命相搏。然而金钱、房子、婚姻等现实的考验，却将两人越推越远。','2025-05-12','爱情','https://ts1.tc.mm.bing.net/th/id/R-C.a5d551a16374c6d4caf84e8f96618844?rik=lf1kYdom2q3pwg&riu=http%3a%2f%2fp2.qhimg.com%2ft010c13ba0088867268.jpg%3f800*1120&ehk=TiOt8cKfsuNDzGV0i5qng3b%2f2ha0clOovC597XXVCK8%3d&risl=&pid=ImgRaw&r=0',NULL,'沙漠',8.4,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(43,'疯狂的外星人','耿浩与一心想发大财的好兄弟大飞，经营着各自惨淡的\"事业\"，然而\"天外来客\"的意外降临，打破了二人平静又拮据的生活。神秘的西方力量也派出\"哼哈二将\"在全球搜查外星人行踪。','2025-05-12','动漫','https://tse2-mm.cn.bing.net/th/id/OIP-C.3ro415AKQ5Wqm79b5Qep-QHaLE?rs=1&pid=ImgDetMain',NULL,'宁浩',8.2,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(44,'上海堡垒','未来世界外星黑暗势力突袭地球，上海成为了人类最后的希望。大学生江洋追随女指挥官林澜进入了上海堡垒成为一名指挥员。外星势力不断发动猛烈袭击，林澜受命保护击退外星人的秘密武器。','2025-05-12','喜剧','https://p1.ssl.qhimg.com/t01cf4f8f52f3f3faa8.jpg',NULL,'滕华涛',8,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(45,'地球脉动','从南极到北极，从赤道到寒带，从非洲草原到热带雨林，再从荒凉峰顶到深邃大海，难以数计的生物以极其绝美的身姿呈现在世人面前。','2025-05-12','自然','https://tse3-mm.cn.bing.net/th/id/OIP-C.rtxF1ADzwIHf5x8USSOYCwHaNK?rs=1&pid=ImgDetMain',NULL,'艾利斯泰尔·福瑟吉尔',9.9,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(46,'蓝色星球','探索海洋的奥秘，从热带珊瑚礁到极地冰层，从浅海到深海，展现海洋生物的多样性和海洋生态系统的复杂性。','2025-05-12','自然','https://puui.qpic.cn/vcover_vt_pic/0/9h9huzlvjs0esjp1506658634/0',NULL,'艾利斯泰尔·福瑟吉尔',9.8,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(47,'我们的星球','从偏远的北极荒野和神秘的深海到广袤的非洲地貌和南美多样化的热带雨林，全面关注全世界生境多样性的广度。','2025-05-12','自然','https://tse3-mm.cn.bing.net/th/id/OIP-C.54cBrlZrk07d_biQpsHdRgHaK-?rs=1&pid=ImgDetMain',NULL,'艾利斯泰尔·福瑟吉尔',9.7,'2025-05-12 14:57:45','2025-05-12 14:57:45'),(48,'冰冻星球','以季节的变化为主线，记录了地球两极在一年内展现出的各种场景，从\"大融化\"的春天，到24小时都在光线照耀下的夏日，再到\"大冰封\"的秋天，最后以长夜漫漫的冬天结尾。','2025-05-12','自然','https://tse1-mm.cn.bing.net/th/id/OIP-C.Lm0dMjnueBEJwRxnyGzpNAHaKY?w=770&h=1080&rs=1&pid=ImgDetMain',NULL,'艾利斯泰尔·福瑟吉尔',9.6,'2025-05-12 14:57:45','2025-05-12 14:57:45');
/*!40000 ALTER TABLE `movie` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movie_category`
--

DROP TABLE IF EXISTS `movie_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movie_category` (
  `movie_id` int(11) NOT NULL,
  `category_id` int(11) NOT NULL,
  PRIMARY KEY (`movie_id`,`category_id`),
  KEY `category_id` (`category_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movie_category`
--

LOCK TABLES `movie_category` WRITE;
/*!40000 ALTER TABLE `movie_category` DISABLE KEYS */;
INSERT INTO `movie_category` VALUES (1,11),(2,12),(3,13),(4,14),(5,15),(6,13),(7,13),(8,12),(9,14),(10,12),(11,16),(12,16),(13,17),(14,17),(15,18),(16,18),(17,19),(18,19),(19,11),(20,11),(21,20),(22,20),(23,20),(24,20),(25,21),(26,22),(27,23),(28,24),(29,25),(30,23),(31,23),(32,22),(33,24),(34,22),(35,26),(36,26),(37,27),(38,27),(39,28),(40,28),(41,29),(42,29),(43,21),(44,21),(45,30),(46,30),(47,30),(48,30);
/*!40000 ALTER TABLE `movie_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review`
--

DROP TABLE IF EXISTS `review`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `review` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text COLLATE utf8_unicode_ci NOT NULL,
  `rating` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `movie_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `movie_id` (`movie_id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review`
--

LOCK TABLES `review` WRITE;
/*!40000 ALTER TABLE `review` DISABLE KEYS */;
/*!40000 ALTER TABLE `review` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8_unicode_ci NOT NULL,
  `password_hash` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  `is_admin` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'movie_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-14 20:38:17
