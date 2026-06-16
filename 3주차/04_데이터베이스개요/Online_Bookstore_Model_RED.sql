
CREATE TABLE Author
(
  Name    varchar(255) NOT NULL,
  Address varchar(255) NOT NULL,
  URL     varchar(255) NULL    ,
  PRIMARY KEY (Name, Address)
);

CREATE TABLE Book
(
  ISBN          varchar(255)   NOT NULL,
  PublisherName varchar(255)   NOT NULL,
  AuthorName    varchar(255)   NOT NULL,
  AuthorAddress varchar(255)   NOT NULL,
  Year          int            NULL    ,
  TItle         varchar(255)   NULL    ,
  Price         numeric(19, 0) NULL    ,
  PRIMARY KEY (ISBN),
  FOREIGN KEY (PublisherName) REFERENCES Publisher (Name),
  FOREIGN KEY (AuthorName, AuthorAddress) REFERENCES Author (Name, Address)
);

CREATE TABLE Customer
(
  Email   varchar(255) NOT NULL,
  Name    varchar(255) NULL    ,
  Phone   varchar(255) NULL    ,
  Address varchar(255) NULL    ,
  PRIMARY KEY (Email)
);

CREATE TABLE Publisher
(
  Name    varchar(255) NOT NULL,
  Address varchar(255) NULL    ,
  Phone   varchar(255) NULL    ,
  URL     int          NULL    ,
  PRIMARY KEY (Name)
);

CREATE TABLE ShoppingBasket
(
  ID            int          NOT NULL,
  CustomerEmail varchar(255) NOT NULL,
  PRIMARY KEY (ID),
  FOREIGN KEY (CustomerEmail) REFERENCES Customer (Email)
);

CREATE TABLE ShoppingBasket_Book
(
  ShoppingBasketID int          NOT NULL,
  BookISBN         varchar(255) NOT NULL,
  Count            int          NULL    ,
  PRIMARY KEY (ShoppingBasketID, BookISBN),
  FOREIGN KEY (BookISBN) REFERENCES Book (ISBN),
  FOREIGN KEY (ShoppingBasketID) REFERENCES ShoppingBasket (ID)
);

CREATE TABLE Warehouse
(
  Code    int          NOT NULL,
  Phone   varchar(255) NULL    ,
  Address varchar(255) NULL    ,
  PRIMARY KEY (Code)
);

CREATE TABLE Warehouse_Book
(
  WarehouseCode int          NOT NULL,
  BookISBN      varchar(255) NOT NULL,
  Count         int          NULL    ,
  PRIMARY KEY (WarehouseCode, BookISBN),
  FOREIGN KEY (BookISBN) REFERENCES Book (ISBN),
  FOREIGN KEY (WarehouseCode) REFERENCES Warehouse (Code)
);
