
CREATE TABLE Match
(
  ID        int          NOT NULL,
  MatchDate datetime     NULL    ,
  Stadium   varchar(255) NULL    ,
  Opponent  varchar(255) NULL    ,
  Own_Score int          NULL    ,
  Opp_Score int          NULL    ,
  PRIMARY KEY (ID)
);

CREATE TABLE Match_Player
(
  MatchID  int         NOT NULL,
  PlayerID int         NOT NULL,
  Score    varchar(10) NULL    ,
  PRIMARY KEY (MatchID, PlayerID),
  FOREIGN KEY (MatchID) REFERENCES Match (ID),
  FOREIGN KEY (PlayerID) REFERENCES Player (ID)
);

CREATE TABLE Player
(
  ID           int          NOT NULL,
  Name         varchar(255) NULL    ,
  Age          int          NULL    ,
  Season_Score int          NULL    ,
  PRIMARY KEY (ID)
);
