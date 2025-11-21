-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: wedcrafts
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `role` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_admins_email` (`email`),
  KEY `ix_admins_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,'WedCraft Admin','admin@wedcraft.com','$2b$12$CwNJQta7PXFtr985QYxsqeK6EZbcIvonImBVGYWpEpvrJvDxyQKbW','admin',1,'2025-11-19 12:08:36');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `event_name` varchar(255) DEFAULT NULL,
  `wedding_date` varchar(20) NOT NULL,
  `location` varchar(500) NOT NULL,
  `google_maps_link` varchar(1000) DEFAULT NULL,
  `custom_invitation_url` varchar(1000) DEFAULT NULL,
  `custom_invitation_file` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_events_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
INSERT INTO `events` VALUES (7,7,'Marriage','2025-11-27','Pala, Kottayam','','http://localhost:8000/test_form.html',NULL,1,'2025-11-20 09:32:28'),(8,7,'New Event','2026-01-01','Kochi, Kerala','','http://localhost:8000/test_form_improved.html',NULL,1,'2025-11-20 10:52:16'),(9,8,'B\'day party ','2025-11-29','Kochi, Kerala','','http://localhost:8000/test_form.html',NULL,1,'2025-11-20 12:23:23'),(10,7,'MRG','2025-11-25','Aluva','','http://localhost:8000/test_form.html',NULL,1,'2025-11-20 12:32:56');
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `family_members`
--

DROP TABLE IF EXISTS `family_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `family_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rsvp_response_id` int NOT NULL,
  `member_name` varchar(255) NOT NULL,
  `food_preference` varchar(20) NOT NULL,
  `is_child` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_family_members_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `family_members`
--

LOCK TABLES `family_members` WRITE;
/*!40000 ALTER TABLE `family_members` DISABLE KEYS */;
INSERT INTO `family_members` VALUES (1,2,'ab','Vegetarian',0,'2025-11-19 13:42:55'),(2,2,'cd','Non-Vegetarian',0,'2025-11-19 13:42:55'),(3,2,'ef','Non-Vegetarian',1,'2025-11-19 13:42:55'),(4,3,'John Doe','Vegetarian',0,'2025-11-19 13:49:01'),(5,3,'Jane Doe','Non-Vegetarian',0,'2025-11-19 13:49:01'),(6,3,'Little Doe','Vegetarian',1,'2025-11-19 13:49:01'),(7,4,'11','Vegetarian',0,'2025-11-19 13:50:28'),(8,4,'12','Non-Vegetarian',1,'2025-11-19 13:50:28'),(9,5,'Alice Smith','Vegetarian',0,'2025-11-19 13:50:42'),(10,5,'Bob Smith','Vegetarian',0,'2025-11-19 13:50:42'),(11,6,'ko','Vegetarian',1,'2025-11-19 13:52:13'),(12,6,'lo','Non-Vegetarian',0,'2025-11-19 13:52:13'),(13,8,'Alice Maybe','Vegetarian',0,'2025-11-19 17:17:11'),(14,8,'Bob Maybe','Non-Vegetarian',0,'2025-11-19 17:17:11'),(15,9,'ggfgf','Vegetarian',0,'2025-11-19 17:26:43'),(16,10,'surya','Non-Vegetarian',1,'2025-11-20 05:30:29'),(17,10,'hari','Non-Vegetarian',0,'2025-11-20 05:30:29'),(18,11,'a','Non-Vegetarian',0,'2025-11-20 05:31:43'),(19,11,'b','Non-Vegetarian',0,'2025-11-20 05:31:43'),(20,11,'c','Vegetarian',1,'2025-11-20 05:31:43'),(21,11,'d','Non-Vegetarian',0,'2025-11-20 05:31:43'),(22,12,'sss','Vegetarian',1,'2025-11-20 06:58:12'),(23,12,'sdsd','Non-Vegetarian',0,'2025-11-20 06:58:12'),(24,12,'sddssd','Non-Vegetarian',0,'2025-11-20 06:58:12'),(25,12,'sd','Non-Vegetarian',0,'2025-11-20 06:58:12'),(26,16,'saasas','Vegetarian',0,'2025-11-20 08:35:46'),(27,17,'a','Non-Vegetarian',0,'2025-11-20 08:36:45'),(28,17,'b','Non-Vegetarian',0,'2025-11-20 08:36:45'),(29,17,'c','Non-Vegetarian',0,'2025-11-20 08:36:45'),(30,17,'ss','Vegetarian',1,'2025-11-20 08:36:45'),(31,18,'hari','Vegetarian',0,'2025-11-20 09:34:12'),(32,18,'vinod','Non-Vegetarian',0,'2025-11-20 09:34:12'),(33,18,'subin','Non-Vegetarian',1,'2025-11-20 09:34:12'),(34,19,'amal','Non-Vegetarian',0,'2025-11-20 10:09:18'),(35,19,'anurag','Non-Vegetarian',0,'2025-11-20 10:09:18'),(36,19,'alen','Non-Vegetarian',0,'2025-11-20 10:09:18'),(37,19,'safal','Vegetarian',1,'2025-11-20 10:09:18'),(38,20,'w','Vegetarian',0,'2025-11-20 11:57:46'),(39,21,'dd','Vegetarian',0,'2025-11-20 12:24:03'),(40,21,'sdfsf','Non-Vegetarian',0,'2025-11-20 12:24:03'),(41,21,'sdf','Non-Vegetarian',0,'2025-11-20 12:24:03'),(42,21,'gfsg','Non-Vegetarian',1,'2025-11-20 12:24:03'),(43,22,'s','Vegetarian',0,'2025-11-20 12:33:32'),(44,22,'sss','Non-Vegetarian',0,'2025-11-20 12:33:32'),(45,22,'gg','Non-Vegetarian',0,'2025-11-20 12:33:32');
/*!40000 ALTER TABLE `family_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `processed_analytics`
--

DROP TABLE IF EXISTS `processed_analytics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `processed_analytics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int DEFAULT NULL,
  `total_families` int DEFAULT NULL,
  `yes_responses` int DEFAULT NULL,
  `no_responses` int DEFAULT NULL,
  `maybe_responses` int DEFAULT NULL,
  `predicted_attendance` int DEFAULT NULL,
  `veg_required` int DEFAULT NULL,
  `nonveg_required` int DEFAULT NULL,
  `children_count` int DEFAULT NULL,
  `attendance_rate` varchar(10) DEFAULT NULL,
  `response_rate` varchar(10) DEFAULT NULL,
  `recommendations` text,
  `processed_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_processed_analytics_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `processed_analytics`
--

LOCK TABLES `processed_analytics` WRITE;
/*!40000 ALTER TABLE `processed_analytics` DISABLE KEYS */;
/*!40000 ALTER TABLE `processed_analytics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rsvp_responses`
--

DROP TABLE IF EXISTS `rsvp_responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rsvp_responses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_id` int NOT NULL,
  `family_name` varchar(255) NOT NULL,
  `attendance` varchar(20) NOT NULL,
  `members_count` int DEFAULT NULL,
  `food_preference` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_rsvp_responses_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rsvp_responses`
--

LOCK TABLES `rsvp_responses` WRITE;
/*!40000 ALTER TABLE `rsvp_responses` DISABLE KEYS */;
INSERT INTO `rsvp_responses` VALUES (18,7,'surya','Yes',3,'Mixed','2025-11-20 09:34:12'),(19,7,'new famly','Maybe',4,'Mixed','2025-11-20 10:09:18'),(20,7,'ss','Yes',1,'Vegetarian','2025-11-20 11:57:46'),(21,7,'ssss','Yes',4,'Mixed','2025-11-20 12:24:03'),(22,10,'sdsdsd','Yes',3,'Mixed','2025-11-20 12:33:32'),(23,2,'Patel Family','Yes',4,'Non-Vegetarian','2025-11-20 19:02:06'),(24,2,'Kumar Family','Yes',3,'Non-Vegetarian','2025-11-20 19:02:06'),(25,2,'Singh Family','Yes',5,'Non-Vegetarian','2025-11-20 19:02:06'),(26,2,'Sharma Family','Yes',2,'Non-Vegetarian','2025-11-20 19:02:06'),(27,2,'Gupta Family','Yes',3,'Non-Vegetarian','2025-11-20 19:02:06'),(28,2,'Reddy Family','Yes',4,'Non-Vegetarian','2025-11-20 19:02:06'),(29,2,'Jain Family','Yes',2,'Vegetarian','2025-11-20 19:02:06'),(30,2,'Agarwal Family','Yes',3,'Vegetarian','2025-11-20 19:02:06'),(31,2,'Mehta Family','Maybe',2,'Vegetarian','2025-11-20 19:02:06'),(32,2,'Shah Family','No',0,NULL,'2025-11-20 19:02:06'),(33,1,'Chopra Family','Yes',4,'Non-Vegetarian','2025-11-20 19:02:06'),(34,1,'Malhotra Family','Yes',3,'Non-Vegetarian','2025-11-20 19:02:06'),(35,1,'Kapoor Family','Yes',2,'Non-Vegetarian','2025-11-20 19:02:06'),(36,1,'Bansal Family','Yes',3,'Vegetarian','2025-11-20 19:02:06'),(37,1,'Mittal Family','Maybe',2,'Vegetarian','2025-11-20 19:02:06');
/*!40000 ALTER TABLE `rsvp_responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `wedding_date` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'John & Sarah Smith','john.sarah@example.com','$2b$12$JbGMnSfJBPUduWJgWZzbWeWeWVM8yVgo.64QZLD1gRpSW0A08o/Lq','user','2024-06-15',1,'2025-11-19 12:08:36'),(4,'suryan','surya@gmail.com','$2b$12$o1Ki.OW/Km5LQiWg1pJdB.FfMPxvdq6DkMnb9tYNehVyibcqdN6dG','user',NULL,1,'2025-11-19 12:11:21'),(5,'Michael Johnson','michael@example.com','$2b$12$jVWgT4xMPnz6aLOHSvIqYuOkvQFi4Tr30q5fao38jGkINImsCvgOy','user','2024-08-20',1,'2025-11-20 07:42:06'),(6,'Emma Wilson','emma@example.com','$2b$12$ROkgdesO2pGDEvczV62/jORwOsW.PWuFlLnjMrG.Qwcj9Df1xZmh2','user','2024-10-12',1,'2025-11-20 07:42:06'),(7,'rahul','rahul@gmail.com','$2b$12$xiMlQ.zOoysxpjlXjza5wuzVSfVkD8mvyqfGjldnwjZm0neUCo2.6','user',NULL,1,'2025-11-20 09:31:08'),(8,'Harikrishnan','hari@gmail.com','$2b$12$TITMSa9Qt.siP7HviYHNwuxbxTERy.KV1wAxNY5.fnCpu5.kZeBPK','user',NULL,1,'2025-11-20 12:22:28');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-21 11:07:30
