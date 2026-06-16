
CREATE TABLE Author
(
  ID        integer NOT NULL,
  Name      varchar NULL    ,
  Email     varchar NULL    ,
  Biography varchar NULL    ,
  PRIMARY KEY (ID)
);

CREATE TABLE Book
(
  ISBN             varchar NOT NULL,
  Title            varchar NULL    ,
  Publication_date date    NULL    ,
  Genre            varchar NULL    ,
  ID               integer NOT NULL,
  ID               integer NOT NULL,
  PRIMARY KEY (ISBN),
  FOREIGN KEY (ID) REFERENCES Author (ID),
  FOREIGN KEY (ID) REFERENCES Customer (ID)
);

CREATE TABLE Customer
(
  ID    integer NOT NULL,
  Name  varchar NULL    ,
  Email varchar NULL    ,
  PRIMARY KEY (ID)
);
