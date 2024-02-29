-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: W-W-System
-- ------------------------------------------------------
-- Server version	8.0.36-0ubuntu0.20.04.1

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
-- Table structure for table `Lagerliste`
--

DROP TABLE IF EXISTS `Lagerliste`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Lagerliste` (
  `Inventarnummer` int NOT NULL,
  `Klinik` varchar(20) DEFAULT NULL,
  `Typ` varchar(20) NOT NULL,
  `Modell` varchar(20) NOT NULL,
  `Spezifikation` tinytext,
  `Investmittel` enum('Ja','Nein','N.A.') NOT NULL,
  `Bestell_Nr.` int NOT NULL,
  `Herausgeber` varchar(35) DEFAULT 'Kein Herausgeber',
  `Ausgabe` datetime DEFAULT NULL,
  `Ausgegeben` enum('1','0') NOT NULL DEFAULT '0',
  PRIMARY KEY (`Inventarnummer`),
  KEY `Bestell_Nr.` (`Bestell_Nr.`),
  KEY `Herausgeber` (`Herausgeber`),
  CONSTRAINT `Lagerliste_ibfk_1` FOREIGN KEY (`Bestell_Nr.`) REFERENCES `Bestell_Liste` (`SAP_Bestell_Nr.`),
  CONSTRAINT `Lagerliste_ibfk_2` FOREIGN KEY (`Herausgeber`) REFERENCES `webapplication_user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `Geliefert` AFTER INSERT ON `Lagerliste` FOR EACH ROW BEGIN
UPDATE `Bestell_Liste`
SET `Geliefert_Anzahl` = (
    SELECT COUNT(`Bestell_Nr.`)
    FROM `Lagerliste`
    WHERE `Bestell_Nr.` = `SAP_Bestell_Nr.`
    AND `Bestell_Liste`.`Geliefert` = '0'
    GROUP BY `Bestell_Nr.`
);
UPDATE `Bestell_Liste`
SET `Geliefert` = '1'
WHERE `Menge` = (
    SELECT COUNT(`Bestell_Nr.`)
    FROM `Lagerliste`
    WHERE `Geliefert` = '0'
    AND `Bestell_Nr.` = `SAP_Bestell_Nr.`
    GROUP BY `Bestell_Nr.`
);
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-02-29  9:05:42
