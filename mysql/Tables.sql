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
    `Preis_pro_Stück` DECIMAL(6, 2) NOT NULL DEFAULT 0,
    `Menge` TINYINT NOT NULL CHECK(`Menge` >= 0),
    `Spezifikation` TINYTEXT,
    `Zuweisung` TINYTEXT,
    `Link` VARCHAR(2083) DEFAULT ' ',
    `Investmittel` ENUM('Ja', 'Nein', 'N.A.') NOT NULL DEFAULT 'N.A.',
    `Inventarnummern Von-Bis` TINYTEXT,
    `Ersteller` VARCHAR(35) DEFAULT 'Kein Ersteller',
    `Bearbeitet` DATETIME,
    `Geliefert` ENUM('1', '0') NOT NULL DEFAULT '0',
    `Geliefert_Anzahl` TINYINT DEFAULT 0,
    PRIMARY KEY(`SAP_Bestell_Nr.`),
    FOREIGN KEY(`Ersteller`) REFERENCES `webapplication_user`(`username`)
);

CREATE TABLE `Investmittelplan` (
    `Klinik_OU` TINYINT NOT NULL,
    `Investmittel_Jahresanfang_in_Euro` DECIMAL(8, 2) NOT NULL CHECK(`Investmittel_Jahresanfang_in_Euro` >= 0) DEFAULT 0,
    `Investmittel_übrig_in_Euro` DECIMAL(9, 2),
    PRIMARY KEY(`Klinik_OU`)
);

CREATE TABLE `Investmittelplan_Soll` (
    `OU` TINYINT NOT NULL,
    `Investmittel_Gesamt` DECIMAL(8, 2) NOT NULL DEFAULT 0,
    `Bereich` VARCHAR(20),
    `Team` VARCHAR(20),
    PRIMARY KEY(`OU`)
);

CREATE TABLE `Detail_Investmittelplan_Soll` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `OU_InvSoll` TINYINT NOT NULL,
    `Typ` VARCHAR(50) NOT NULL,
    `Modell` VARCHAR(50) NOT NULL,
    `Spezifikation` TINYTEXT,
    `Menge` TINYINT NOT NULL DEFAULT 0,
    `Preis_pro_Stück` DECIMAL(6, 2) NOT NULL DEFAULT 0,
    `Admin` VARCHAR(35) DEFAULT 'Kein Ersteller',
    PRIMARY KEY(`id`),
    FOREIGN KEY(`Admin`) REFERENCES `webapplication_user`(`username`),
    FOREIGN KEY(`OU_InvSoll`) REFERENCES `Investmittelplan_Soll`(`OU`)
);
    
CREATE TABLE `Test` ( 
    `Klinik_OU` TINYINT NOT NULL, 
    `Investmittel_Jahresanfang_in_Euro` DECIMAL(8, 2) NOT NULL DEFAULT 0, 
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
