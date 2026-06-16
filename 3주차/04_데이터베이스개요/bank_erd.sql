
CREATE TABLE Account
(
  account_id INTEGER NOT NULL,
  Name       VARCHAR NULL    ,
  ID         INTEGER NOT NULL,
  ID         INTEGER NOT NULL,
  PRIMARY KEY (account_id)
);

CREATE TABLE Customer
(
  ID              INTEGER NOT NULL,
  Name            VARCHAR NOT NULL DEFAULT 홍길동,
  Account_Number  VARCHAR NOT NULL,
  PIN             VARCHAR NULL    ,
  Account_Balance DECIMAL NULL    ,
  PRIMARY KEY (ID)
);

ALTER TABLE Account
  ADD CONSTRAINT FK_Customer_TO_Account
    FOREIGN KEY (ID)
    REFERENCES Customer (ID);
