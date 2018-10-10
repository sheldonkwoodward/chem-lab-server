#Delete and recreate database

DROP DATABASE IF EXISTS `chemlab`;

CREATE DATABASE IF NOT EXISTS `chemlab`;

USE chemlab;

#Create tables

CREATE TABLE IF NOT EXISTS `students` (
  `student_id` VARCHAR(7) NOT NULL,
  `first_name` VARCHAR(25) NOT NULL,
  `last_name` VARCHAR(25) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  PRIMARY KEY(`student_id`)
);

CREATE TABLE IF NOT EXISTS `courses` (
  `course_id` VARCHAR(7) NOT NULL,
  `course_name` VARCHAR(25) NOT NULL,
  PRIMARY KEY(`course_id`)
);

CREATE TABLE IF NOT EXISTS `enrolled` (
  `student_id` VARCHAR(7) NOT NULL,
  `course_id` VARCHAR(7) NOT NULL,
  FOREIGN KEY(`student_id`)
    REFERENCES students(`student_id`)
    ON DELETE CASCADE,
  FOREIGN KEY(`course_id`)
    REFERENCES courses(`course_id`)
    ON DELETE CASCADE
);


#Insert test data

INSERT INTO `students` (`student_id`, `first_name`, `last_name`, `email`) VALUES
('2000001', 'John', 'Doe', 'john.doe@wallawalla.edu');

INSERT INTO `courses` (`course_id`, `course_name`) VALUES
('CHEM101', 'Intro to Chemestry');

INSERT INTO `enrolled` (`student_id`, `course_id`) VALUES
('2000001', 'CHEM101');
