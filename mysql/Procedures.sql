CREATE PROCEDURE `Geliefert`()
BEGIN
SELECT `SAP_Bestell_Nr.`
FROM `Bestell_Liste` WHERE `Geliefert` = '1';
END//

CREATE PROCEDURE `Ausgegeben`()
BEGIN
SELECT `Inventarnummer`, `Klinik`, `Ausgabe`
FROM `Lagerliste` WHERE `Ausgegeben` = '1';
END//

CREATE PROCEDURE `Lagerliste_Default`()
BEGIN
SELECT COUNT(`Bestell_Nr.`) AS 'Menge', `Bestell_Nr.`, `Modell`, `Typ`, `Spezifikation`, `Investmittel`
FROM `Lagerliste` WHERE `Ausgegeben` = '0'
GROUP BY `Bestell_Nr.`, `Modell`, `Typ`, `Spezifikation`, `Investmittel`;
END//

CREATE PROCEDURE `Bestell_Liste_Default`()
BEGIN
SELECT `SAP_Bestell_Nr.`, `Modell`, `Typ`, `Menge`, `Spezifikation`, `Inventarnummern Von-Bis`, `Geliefert_Anzahl`
FROM `Bestell_Liste` WHERE `Geliefert` = '0';
END//
