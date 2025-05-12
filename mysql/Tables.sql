CREATE TABLE `Lagerliste` (
    `Inventarnummer` VARCHAR(20) NOT NULL,
    `Klinik` TINYINT,
    `Typ` VARCHAR(50) NOT NULL,
    `Modell` VARCHAR(50) NOT NULL,
    `Spezifikation` TINYTEXT,
    `Zuweisung` TINYTEXT,
    `Bestell_Nr.` VARCHAR(20) NOT NULL ,
    `Herausgeber` VARCHAR(35) DEFAULT 'Kein Herausgeber',
    `Ausgabe` DATETIME,
    `Ausgegeben` ENUM('1', '0') NOT NULL DEFAULT '0',
    PRIMARY KEY(`Inventarnummer`),
    FOREIGN KEY(`Bestell_Nr.`) REFERENCES `Bestell_Liste`(`SAP_Bestell_Nr.`),
    FOREIGN KEY(`Herausgeber`) REFERENCES `webapplication_user`(`username`)
);

CREATE TABLE `Bestell_Liste` (
    `SAP_Bestell_Nr.` VARCHAR(20) NOT NULL,
    `Modell` VARCHAR(50) NOT NULL,
    `Typ` VARCHAR(50) NOT NULL,
    `Preis_pro_Stück` DECIMAL(8, 2) NOT NULL DEFAULT 0,
    `Menge` TINYINT UNSIGNED NOT NULL CHECK(`Menge` >= 0),
    `Spezifikation` TINYTEXT,
    `Zuweisung` TINYTEXT,
    `Link` VARCHAR(2083) DEFAULT ' ',
    `Investmittel` ENUM('Ja', 'Nein', 'N.A.') NOT NULL DEFAULT 'N.A.',
    `Inventarnummern Von-Bis` TINYTEXT,
    `Ersteller` VARCHAR(35) DEFAULT 'Kein Ersteller',
    `Bearbeitet` DATETIME,
    `Geliefert` ENUM('1', '0') NOT NULL DEFAULT '0',
    `Geliefert_Anzahl` SMALLINT DEFAULT 0,
    PRIMARY KEY(`SAP_Bestell_Nr.`),
    FOREIGN KEY(`Ersteller`) REFERENCES `webapplication_user`(`username`)
);

CREATE TABLE `Investmittelplan` (
    `Klinik_OU` TINYINT NOT NULL,
    `Investmittel_Jahresanfang_in_Euro` DECIMAL(10, 2) NOT NULL CHECK(`Investmittel_Jahresanfang_in_Euro` >= 0) DEFAULT 0,
    `Investmittel_übrig_in_Euro` DECIMAL(10, 2),
    PRIMARY KEY(`Klinik_OU`)
);

CREATE TABLE `Investmittelplan_Soll` (
    `OU` TINYINT NOT NULL,
    `Investmittel_Gesamt` DECIMAL(10, 2) NOT NULL DEFAULT 0,
    `Bereich` VARCHAR(40),
    `Team` VARCHAR(20),
    PRIMARY KEY(`OU`)
);

CREATE TABLE `Detail_Investmittelplan_Soll` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `OU_InvSoll` TINYINT NOT NULL,
    `Typ` VARCHAR(50) NOT NULL,
    `Modell` VARCHAR(50) NOT NULL,
    `Spezifikation` TINYTEXT,
    `Menge` TINYINT UNSIGNED NOT NULL DEFAULT 0,
    `Preis_pro_Stück` DECIMAL(8, 2) NOT NULL DEFAULT 0,
    `Admin` VARCHAR(35) DEFAULT 'Kein Ersteller',
    PRIMARY KEY(`id`),
    FOREIGN KEY(`Admin`) REFERENCES `webapplication_user`(`username`),
    FOREIGN KEY(`OU_InvSoll`) REFERENCES `Investmittelplan_Soll`(`OU`)
);
    
CREATE TABLE `Test` ( 
    `Klinik_OU` TINYINT NOT NULL, 
    `Investmittel_Jahresanfang_in_Euro` DECIMAL(10, 2) NOT NULL DEFAULT 0,
    `Investmittel_übrig_in_Euro` DECIMAL(10, 2),
    PRIMARY KEY(`Klinik_OU`) 
);

CREATE TABLE `Lagerliste_ohne_Invest` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `Typ` VARCHAR(50) NOT NULL,
    `Modell` VARCHAR(50) NOT NULL,
    `Spezifikation` TINYTEXT,
    `Bestell_Nr.` VARCHAR(20) NOT NULL,
    `Herausgeber` VARCHAR(35) DEFAULT 'Kein Herausgeber',
    `Ausgabe` DATETIME,
    `Ausgegeben` ENUM('1', '0') NOT NULL DEFAULT '0',
    PRIMARY KEY(`id`),
    FOREIGN KEY(`Herausgeber`) REFERENCES `webapplication_user`(`username`),
    FOREIGN KEY(`Bestell_Nr.`) REFERENCES `Bestell_Liste`(`SAP_Bestell_Nr.`)
);

CREATE TABLE `Achievements` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `User` VARCHAR(35) NOT NULL,
    `Bestell_Count` INT DEFAULT 0,
    `Bestell_Achievement` TINYINT DEFAULT 0,
    `Lager_Count` INT DEFAULT 0,
    `Lager_Achievement` TINYINT DEFAULT 0,
    `Rueckgabe_Count` INT DEFAULT 0,
    `Rueckgabe_Achievement` TINYINT DEFAULT 0,
    `Handout_Count` INT DEFAULT 0,
    `Handout_Achievement` TINYINT DEFAULT 0,
    `Update_Achievement` TINYINT DEFAULT 0,
    PRIMARY KEY(`id`),
    FOREIGN KEY(`User`) REFERENCES `webapplication_user`(`username`)
);

CREATE Table `OU` (
`OU_id` INT NOT NULL AUTO_INCREMENT,
`OU` INT NOT NULL,
PRIMARY KEY(`OU_id`)
);

CREATE Table `Invest` ( 
`id` INT NOT NULL AUTO_INCREMENT, 
`ou_id` INT NOT NULL, 
`investmittel_übrig` DECIMAL(8, 2) NOT NULL DEFAULT 0, 
`investmittel_gesamt` DECIMAL(8, 2) DEFAULT 0, 
`team` VARCHAR(20), 
`bereich` VARCHAR(40), 
`jahr` INT NOT NULL, 
`typ` VARCHAR (20) NOT NULL,
PRIMARY KEY(`id`), 
FOREIGN KEY(`ou_id`) REFERENCES `OU`(`OU_id`) );
