-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: paragonapartments
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apartments`
--

DROP TABLE IF EXISTS `apartments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartments` (
  `apartment_ID` int NOT NULL AUTO_INCREMENT,
  `location_ID` int DEFAULT NULL,
  `apartment_address` varchar(45) DEFAULT NULL,
  `number_of_beds` int DEFAULT NULL,
  `monthly_rent` float DEFAULT NULL,
  `occupied` tinyint DEFAULT '0',
  PRIMARY KEY (`apartment_ID`),
  UNIQUE KEY `apartment_ID_UNIQUE` (`apartment_ID`),
  KEY `location_IDa` (`location_ID`),
  CONSTRAINT `location_IDa` FOREIGN KEY (`location_ID`) REFERENCES `locations` (`location_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartments`
--

LOCK TABLES `apartments` WRITE;
/*!40000 ALTER TABLE `apartments` DISABLE KEYS */;
INSERT INTO `apartments` VALUES (1,1,'Apartment 1',1,850,1),(2,1,'Apartment 2',2,1050,1),(3,1,'Apartment 3',3,1350,1),(4,1,'Apartment 4',2,1100,1),(5,1,'Apartment 5',1,900,1),(6,1,'Apartment 6',2,1000,0),(7,1,'Apartment 7',1,820,0),(8,1,'Apartment 8',3,1400,0),(9,2,'Apartment 1',1,700,1),(10,2,'Apartment 2',2,850,1),(11,2,'Apartment 3',3,1100,1),(12,2,'Apartment 4',2,900,1),(13,2,'Apartment 5',1,750,1),(14,2,'Apartment 6',2,830,0),(15,2,'Apartment 7',1,680,0),(16,2,'Apartment 8',3,1150,0),(17,3,'Apartment 1',1,1300,1),(18,3,'Apartment 2',2,1700,1),(19,3,'Apartment 3',3,2200,1),(20,3,'Apartment 4',2,1800,1),(21,3,'Apartment 5',1,1400,1),(22,3,'Apartment 6',2,1650,0),(23,3,'Apartment 7',1,1250,0),(24,3,'Apartment 8',3,2300,0),(25,4,'Apartment 1',1,800,1),(26,4,'Apartment 2',2,950,1),(27,4,'Apartment 3',3,1200,1),(28,4,'Apartment 4',2,1000,1),(29,4,'Apartment 5',1,850,1),(30,4,'Apartment 6',2,920,0),(31,4,'Apartment 7',1,780,0),(32,4,'Apartment 8',3,1250,0);
/*!40000 ALTER TABLE `apartments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaint`
--

DROP TABLE IF EXISTS `complaint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `complaint` (
  `complaint_ID` int NOT NULL AUTO_INCREMENT,
  `tenant_ID` int DEFAULT NULL,
  `description` longtext,
  `date_submitted` date DEFAULT NULL,
  `resolved` tinyint DEFAULT '0',
  PRIMARY KEY (`complaint_ID`),
  UNIQUE KEY `complaint_ID_UNIQUE` (`complaint_ID`),
  KEY `tenant_IDc` (`tenant_ID`),
  CONSTRAINT `tenant_IDc` FOREIGN KEY (`tenant_ID`) REFERENCES `tenants` (`tenant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint`
--

LOCK TABLES `complaint` WRITE;
/*!40000 ALTER TABLE `complaint` DISABLE KEYS */;
/*!40000 ALTER TABLE `complaint` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `invoice_ID` int NOT NULL AUTO_INCREMENT,
  `tenant_ID` int DEFAULT NULL,
  `amount_due` float DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `issue_date` date DEFAULT NULL,
  `paid` tinyint DEFAULT '0',
  PRIMARY KEY (`invoice_ID`),
  UNIQUE KEY `invoice_ID_UNIQUE` (`invoice_ID`),
  KEY `tenant_ID` (`tenant_ID`),
  CONSTRAINT `tenant_IDi` FOREIGN KEY (`tenant_ID`) REFERENCES `tenants` (`tenant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lease_agreements`
--

DROP TABLE IF EXISTS `lease_agreements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lease_agreements` (
  `lease_ID` int NOT NULL AUTO_INCREMENT,
  `tenant_ID` int DEFAULT NULL,
  `apartment_ID` int DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `monthly_rent` float DEFAULT NULL,
  `active` tinyint DEFAULT '1',
  PRIMARY KEY (`lease_ID`),
  UNIQUE KEY `lease_ID_UNIQUE` (`lease_ID`),
  KEY `tenant_ID` (`tenant_ID`),
  KEY `apartment_ID` (`apartment_ID`),
  CONSTRAINT `apartment_IDl` FOREIGN KEY (`apartment_ID`) REFERENCES `apartments` (`apartment_ID`),
  CONSTRAINT `tenant_IDl` FOREIGN KEY (`tenant_ID`) REFERENCES `tenants` (`tenant_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lease_agreements`
--

LOCK TABLES `lease_agreements` WRITE;
/*!40000 ALTER TABLE `lease_agreements` DISABLE KEYS */;
INSERT INTO `lease_agreements` VALUES (1,1,1,'2024-01-01','2025-01-01',850,1),(2,2,2,'2024-02-01','2025-02-01',750,1),(3,3,3,'2024-03-01','2025-03-01',1100,1),(4,4,4,'2024-01-15','2025-01-15',900,1),(5,5,5,'2024-04-01','2025-04-01',700,1),(6,6,9,'2024-02-01','2025-02-01',780,1),(7,7,10,'2024-03-01','2025-03-01',680,1),(8,8,11,'2024-01-01','2025-01-01',1000,1),(9,9,12,'2024-04-15','2025-04-15',820,1),(10,10,13,'2024-05-01','2025-05-01',650,1),(11,11,17,'2024-01-01','2025-01-01',1500,1),(12,12,18,'2024-02-01','2025-02-01',1300,1),(13,13,19,'2024-03-01','2025-03-01',2000,1),(14,14,20,'2024-04-01','2025-04-01',1700,1),(15,15,21,'2024-05-01','2025-05-01',1200,1),(16,16,25,'2024-01-01','2025-01-01',900,1),(17,17,26,'2024-02-01','2025-02-01',780,1),(18,18,27,'2024-03-01','2025-03-01',1150,1),(19,19,28,'2024-04-01','2025-04-01',950,1),(20,20,29,'2024-05-01','2025-05-01',720,1);
/*!40000 ALTER TABLE `lease_agreements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `location_ID` int NOT NULL AUTO_INCREMENT,
  `city` varchar(45) DEFAULT NULL,
  `address` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`location_ID`),
  UNIQUE KEY `location_ID_UNIQUE` (`location_ID`),
  UNIQUE KEY `city_UNIQUE` (`city`),
  UNIQUE KEY `address_UNIQUE` (`address`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locations`
--

LOCK TABLES `locations` WRITE;
/*!40000 ALTER TABLE `locations` DISABLE KEYS */;
INSERT INTO `locations` VALUES (1,'Bristol','12 Broadmead, Bristol, BS2 ZPK'),(2,'Cardiff','15 Tredegar St, Cardiff, CF5Z 6GP'),(3,'London','18 Rupert St, London, EC1A 6IQ'),(4,'Manchester','23 Corporation St, Manchester, M3T 3AM');
/*!40000 ALTER TABLE `locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maintenance_requests`
--

DROP TABLE IF EXISTS `maintenance_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_requests` (
  `request_ID` int NOT NULL AUTO_INCREMENT,
  `apartment_ID` int DEFAULT NULL,
  `tenant_ID` int DEFAULT NULL,
  `issue_description` longtext,
  `priority_level` int DEFAULT NULL,
  `reported_date` date DEFAULT NULL,
  `scheduled_date` date DEFAULT NULL,
  `completed` tinyint DEFAULT '0',
  `cost` float DEFAULT NULL,
  PRIMARY KEY (`request_ID`),
  UNIQUE KEY `request_ID_UNIQUE` (`request_ID`),
  KEY `apartment_ID` (`apartment_ID`),
  KEY `tenant_ID` (`tenant_ID`),
  CONSTRAINT `apartment_IDm` FOREIGN KEY (`apartment_ID`) REFERENCES `apartments` (`apartment_ID`),
  CONSTRAINT `tenant_IDm` FOREIGN KEY (`tenant_ID`) REFERENCES `tenants` (`tenant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_requests`
--

LOCK TABLES `maintenance_requests` WRITE;
/*!40000 ALTER TABLE `maintenance_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `maintenance_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `payment_ID` int NOT NULL AUTO_INCREMENT,
  `invoice_ID` int DEFAULT NULL,
  `tenant_ID` int DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `amount` float DEFAULT NULL,
  PRIMARY KEY (`payment_ID`),
  UNIQUE KEY `payment_ID_UNIQUE` (`payment_ID`),
  KEY `invoice_ID` (`invoice_ID`) /*!80000 INVISIBLE */,
  KEY `tenant_ID` (`tenant_ID`),
  CONSTRAINT `invoice_IDp` FOREIGN KEY (`invoice_ID`) REFERENCES `invoices` (`invoice_ID`),
  CONSTRAINT `tenant_IDp` FOREIGN KEY (`tenant_ID`) REFERENCES `tenants` (`tenant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tenants`
--

DROP TABLE IF EXISTS `tenants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tenants` (
  `tenant_ID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `NI_number` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `phone` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tenant_ID`),
  UNIQUE KEY `tenant_ID_UNIQUE` (`tenant_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tenants`
--

LOCK TABLES `tenants` WRITE;
/*!40000 ALTER TABLE `tenants` DISABLE KEYS */;
INSERT INTO `tenants` VALUES (1,'Alice Brown','AB123456A','alice.brown@demo.com','07111111111'),(2,'James Wilson','JW234567B','james.wilson@demo.com','07111111112'),(3,'Emily Carter','EC345678C','emily.carter@demo.com','07111111113'),(4,'Michael Green','MG456789D','michael.green@demo.com','07111111114'),(5,'Sophie Taylor','ST567890E','sophie.taylor@demo.com','07111111115'),(6,'Daniel Harris','DH678901F','daniel.harris@demo.com','07222222221'),(7,'Olivia Martin','OM789012G','olivia.martin@demo.com','07222222222'),(8,'Thomas Lewis','TL890123H','thomas.lewis@demo.com','07222222223'),(9,'Lucy Walker','LW901234I','lucy.walker@demo.com','07222222224'),(10,'Ben Scott','BS012345J','ben.scott@demo.com','07222222225'),(11,'Harry King','HK112233A','harry.king@demo.com','07333333331'),(12,'Amelia Wright','AW223344B','amelia.wright@demo.com','07333333332'),(13,'Jack Turner','JT334455C','jack.turner@demo.com','07333333333'),(14,'Isla Patel','IP445566D','isla.patel@demo.com','07333333334'),(15,'Noah Ahmed','NA556677E','noah.ahmed@demo.com','07333333335'),(16,'Liam ONeill','LO667788F','liam.oneill@demo.com','07444444441'),(17,'Mia Roberts','MR778899G','mia.roberts@demo.com','07444444442'),(18,'Ethan Wood','EW889900H','ethan.wood@demo.com','07444444443'),(19,'Grace Hall','GH990011I','grace.hall@demo.com','07444444444'),(20,'Oliver Price','OP001122J','oliver.price@demo.com','07444444445');
/*!40000 ALTER TABLE `tenants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_ID` int NOT NULL AUTO_INCREMENT,
  `location_ID` int DEFAULT NULL,
  `username` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `role` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`user_ID`),
  UNIQUE KEY `user_ID_UNIQUE` (`user_ID`),
  KEY `location_ID` (`location_ID`),
  CONSTRAINT `location_IDu` FOREIGN KEY (`location_ID`) REFERENCES `locations` (`location_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,NULL,'manager','paragon1','manager'),(2,1,'bristol_admin','admin1','admin'),(3,NULL,'finance','finance1','finance'),(4,1,'bristol_frontdesk','front1','frontdesk'),(5,1,'bristol_maintenance','maint1','maintenance'),(6,NULL,'guest','guest1',NULL),(7,2,'cardiff_admin','admin1','admin'),(8,2,'cardiff_frontdesk','front1','frontdesk'),(9,2,'cardiff_maintenance','maint1','maintenance'),(10,3,'london_admin','admin1','admin'),(11,3,'london_frontdesk','front1','frontdesk'),(12,3,'london_maintenance','maint1','maintenance'),(13,4,'manchester_admin','admin1','admin'),(14,4,'manchester_frontdesk','front1','frontdesk'),(15,4,'manchester_maintenance','maint1','maintenance');
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

-- Dump completed on 2025-12-15 14:10:06
