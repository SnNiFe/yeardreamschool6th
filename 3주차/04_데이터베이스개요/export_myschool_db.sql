
CREATE TABLE course
(
  course_id    VARCHAR(10)  NULL    ,
  title        VARCHAR(100) NOT NULL,
  credit       INT          NOT NULL,
  prof_id      VARCHAR(10)  NULL    ,
  max_students INT          NULL     DEFAULT 30
);

CREATE TABLE department
(
  dept_id   VARCHAR(10) NULL    ,
  dept_name VARCHAR(50) NOT NULL,
  location  VARCHAR(50) NULL     DEFAULT 미정,
  PRIMARY KEY (dept_id)
);

CREATE TABLE enrollment
(
  student_id  VARCHAR(10) NULL    ,
  course_id   VARCHAR(10) NULL    ,
  enroll_date DATE        NOT NULL,
  score       INT         NULL    
);

CREATE TABLE professor
(
  prof_id   VARCHAR(10) NULL    ,
  name      VARCHAR(20) NOT NULL,
  email     VARCHAR(50) NOT NULL UNIQUE,
  dept_id   VARCHAR(10) NULL    ,
  hire_year INT         NULL    ,
  PRIMARY KEY (prof_id),
  FOREIGN KEY (dept_id) REFERENCES department (dept_id)
);

CREATE TABLE student
(
  student_id   VARCHAR(10) NULL    ,
  name         VARCHAR(20) NOT NULL,
  email        VARCHAR(50) NULL     UNIQUE,
  birth_year   INT         NULL    ,
  dept_id      VARCHAR(10) NULL    ,
  grade        INT         NULL    ,
  tuition_paid VARCHAR(1)  NULL     DEFAULT N,
  PRIMARY KEY (student_id),
  FOREIGN KEY (dept_id) REFERENCES department (dept_id)
);
