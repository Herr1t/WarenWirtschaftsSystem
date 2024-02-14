CREATE TABLE `Lagerliste` (
    `Inventarnummer` INT NOT NULL,
    `Klinik` VARCHAR(20),
    `Typ` VARCHAR(20) NOT NULL,
    `Modell` VARCHAR(20) NOT NULL,
    `Spezifikation` TINYTEXT,
    `Investmittel` ENUM('Ja', 'Nein') NOT NULL,
    `Bestell_Nr.` INT NOT NULL ,
    `Ausgabe` DATETIME,
    `Ausgegeben` ENUM('1', '0') NOT NULL DEFAULT '0',
    PRIMARY KEY(`Inventarnummer`),
    FOREIGN KEY(`Bestell_Nr.`) REFERENCES `Bestell_Liste`(`SAP_Bestell_Nr.`)
);

CREATE TABLE `Bestell_Liste` (
    `SAP_Bestell_Nr.` INT NOT NULL,
    `Modell` VARCHAR(20) NOT NULL,
    `Typ` VARCHAR(20) NOT NULL,
    `Menge` TINYINT NOT NULL CHECK(`Menge` >= 0),
    `Spezifikation` TINYTEXT,
    `Inventarnummern Von-Bis` TINYTEXT,
    `Geliefert` ENUM('1', '0') NOT NULL DEFAULT '0',
    `Geliefert_Anzahl` TINYINT DEFAULT 0,
    PRIMARY KEY(`SAP_Bestell_Nr.`)
);

CREATE TABLE `Investmittelplan` (
    `Klinik_OU` VARCHAR(3) NOT NULL,
    `Investmittel_Jahresanfang_in_Euro` DECIMAL(6, 2) NOT NULL CHECK(`Investmittel_Jahresanfang_in_Euro` >= 0) DEFAULT 0,
    `Investmittel_übrig_in_Euro` DECIMAL(6, 2) CHECK(`Investmittel_übrig_in_Euro` >= 0),
    PRIMARY KEY(`Klinik_OU`)
);