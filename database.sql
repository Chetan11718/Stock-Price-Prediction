use all_companies_data1;
-- select * from companies_data;
ALTER TABLE companies_data ADD COLUMN HighestInNext1Week_A float;
ALTER TABLE companies_data ADD COLUMN HighestInNext2Weeks_A float;
ALTER TABLE companies_data ADD COLUMN LowestInNext1Week_A float;
ALTER TABLE companies_data ADD COLUMN LowestInNext2Weeks_A float;
ALTER TABLE companies_data ADD COLUMN HighestInNext1Week_P float;
ALTER TABLE companies_data ADD COLUMN HighestInNext2Weeks_P float;
ALTER TABLE companies_data ADD COLUMN LowestInNext1Week_P float;
ALTER TABLE companies_data ADD COLUMN LowestInNext2Weeks_P float;

CREATE TABLE `parameters` (
  `symbol` varchar(20) NOT NULL,
  `company` varchar(50) DEFAULT NULL,
  `minweeks` int DEFAULT NULL,
  `maxweeks` int DEFAULT NULL,
  `threshold_percentage` float DEFAULT NULL,
  PRIMARY KEY (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("TCS","Tata Consultancy Services",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("SBIN","State Bank of India",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("KOTAKBANK","Kotak Mahindra Bank",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("ITC","ITC",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("INFY","Infosys",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("HINDUNILVR","Hindustan Unilever",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("HDFCBANK","HDFC Bank",29,30,2);


INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("COALINDIA","Coal India",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("BHARTIARTL","Bharti Airtel",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("BAJFINANCE","Bajaj Finance",29,30,2);

INSERT INTO `parameters`
(`symbol`,
`company`,
`minweeks`,
`maxweeks`,
`threshold_percentage`)
VALUES
("ADANIPORTS","Adani Ports and Special Economic Zone",29,30,2);




