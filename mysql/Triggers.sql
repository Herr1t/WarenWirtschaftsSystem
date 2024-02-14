CREATE TRIGGER `Geliefert`
AFTER INSERT ON `Lagerliste`
FOR EACH ROW
BEGIN
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
END//

CREATE TRIGGER `Investmittel_Abrechnung`
BEFORE UPDATE ON `Investmittelplan`
FOR EACH ROW
BEGIN
IF NEW.`Investmittel_übrig_in_Euro` IS NULL THEN
SET NEW.`Investmittel_übrig_in_Euro` := NEW.`Investmittel_Jahresanfang_in_Euro`;
END IF;
END//
