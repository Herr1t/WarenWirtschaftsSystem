INSERT INTO `Bestell_Liste` (`SAP_Bestell_Nr.`, `Modell`, `Typ`, `Menge`, `Spezifikation`, `Inventarnummern Von-Bis`)
VALUES ('57758668', 'D759', 'Monitor', '50', '27"', '234567 - 234617');

CREATE PROCEDURE `Insert_Lagerliste`()
BEGIN
DECLARE i int DEFAULT 234618;
WHILE i <= 234624 DO
INSERT INTO `Lagerliste` (`Inventarnummer`, `Typ`, `Modell`, `Spezifikation`, `Investmittel`, `Bestell_Nr.`)
VALUES (i, 'Kabel', 'HDMI-Kabel', '2m', 'Ja', '239775');
SET i = i + 1;
END WHILE;
END//

INSERT INTO `Bestell_Liste` (`SAP_Bestell_Nr.`, `Modell`, `Typ`, `Menge`, `Spezifikation`, `Inventarnummern Von-Bis`)
VALUES ('239775', 'HDMI-Kabel', 'Kabel', '10', '2m', '234618 - 234627');

/* Laden von CSV
LOAD DATA INFILE 'path/to/csv'
INTO TABLE `Bestell_Liste`
FIELDS TERMINATED BY ',';
*/

CREATE PROCEDURE `Insert`()
BEGIN
DECLARE i int DEFAULT 1;
WHILE i <= 99 DO
INSERT INTO `Investmittelplan` (`Klinik_OU`)
VALUES (i);
SET i = i + 1;
END WHILE;
END//

LOAD DATA INFILE '/var/lib/mysql-files/Invest 2024.csv' INTO TABLE `Test` FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

UPDATE Investmittelplan AS s JOIN Test AS t ON t.Klinik_OU=s.Klinik_OU SET s.Investmittel_Jahresanfang_in_Euro=t.Investmittel_Jahresanfang_in_Euro;
UPDATE Investmittelplan AS s JOIN Test AS t ON t.Klinik_OU=s.Klinik_OU SET s.Investmittel_übrig_in_Euro=t.Investmittel_übrig_in_Euro;
