
CREATE TABLE ATM
(
  ID       INTEGER NOT NULL,
  Location VARCHAR NULL    ,
  PRIMARY KEY (ID),
  FOREIGN KEY (ID) REFERENCES Transaction (ID)
);

CREATE TABLE Customer
(
  ID              INTEGER NOT NULL,
  Name            VARCHAR NOT NULL,
  Account_Number  VARCHAR NOT NULL,
  PIN             VARCHAR NULL    ,
  Account_Balance DECIMAL NULL    ,
  PRIMARY KEY (ID)
);

CREATE TABLE Transaction
(
  ID     INTEGER NOT NULL,
  Date   DATE    NULL    ,
  Time   TIME    NULL    ,
  Amount DECIMAL NOT NULL,
  PRIMARY KEY (ID),
  FOREIGN KEY (ID) REFERENCES Customer (ID)
);
