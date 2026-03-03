d/* ================================
   DATABASE CREATION
   ================================ */

CREATE DATABASE IF NOT EXISTS voting_system;
USE voting_system;

/* ================================
   USERS TABLE
   ================================ */

CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    pwd VARCHAR(255) NOT NULL,
    adharId VARCHAR(25) NOT NULL,
    voterID VARCHAR(25) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    is_voted TINYINT(1) NOT NULL DEFAULT 0,
    voted_condi TINYINT(1) NOT NULL DEFAULT 0,
    role ENUM('admin','voter') NOT NULL DEFAULT 'voter',
    PRIMARY KEY (user_id),
    UNIQUE (adharId),
    UNIQUE (voterID)
);

/* ================================
   CANDIDATES TABLE
   ================================ */


/* ================================
   DEFAULT ADMIN USER (OPTIONAL)
   ================================ */

INSERT  INTO users 
(username, pwd, adharId, voterID, gender, role)
VALUES
('admin', 'admin123', '000000000000', 'ADMIN001', 'NA', 'admin');

use voting_system;
select * from users;



CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10),
    party_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(100),
    voter INT NOT NULL DEFAULT 0,
    PRIMARY KEY (candidate_id)
);


INSERT INTO candidates (name, age, gender, party_name, symbol, voter) VALUES
('Amit Sharma', 45, 'Male', 'National Unity Party', 'Lion', 0),
('Priya Verma', 38, 'Female', 'People First Party', 'Lotus', 0),
('Rahul Singh', 50, 'Male', 'Democratic Front', 'Hand', 0),
('Neha Gupta', 35, 'Female', 'Green Future Party', 'Tree', 0),
('Vikram Patel', 42, 'Male', 'Progressive Alliance', 'Wheel', 0);


INSERT INTO users (username, pwd, adharId, voterID, gender, is_voted, voted_condi, role) VALUES


('rahul', 'pass123', 'AADH1000002', 'VOTER100002', 'Male', 0, 0, 'voter'),
('priya', 'pass123', 'AADH1000003', 'VOTER100003', 'Female', 0, 0, 'voter'),
('amit', 'pass123', 'AADH1000004', 'VOTER100004', 'Male', 0, 0, 'voter'),
('neha', 'pass123', 'AADH1000005', 'VOTER100005', 'Female', 0, 0, 'voter'),
('vikram', 'pass123', 'AADH1000006', 'VOTER100006', 'Male', 0, 0, 'voter'),
('kavita', 'pass123', 'AADH1000007', 'VOTER100007', 'Female', 0, 0, 'voter'),
('suresh', 'pass123', 'AADH1000008', 'VOTER100008', 'Male', 0, 0, 'voter'),
('sunita', 'pass123', 'AADH1000009', 'VOTER100009', 'Female', 0, 0, 'voter'),
('rohit', 'pass123', 'AADH1000010', 'VOTER100010', 'Male', 0, 0, 'voter'),
('anita', 'pass123', 'AADH1000011', 'VOTER100011', 'Female', 0, 0, 'voter');
