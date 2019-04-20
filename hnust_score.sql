/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50721
Source Host           : localhost:3306
Source Database       : hnust_score

Target Server Type    : MYSQL
Target Server Version : 50721
File Encoding         : 65001

Date: 2019-04-20 12:56:15
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for score_info
-- ----------------------------
DROP TABLE IF EXISTS `score_info`;
CREATE TABLE `score_info` (
  `id` varchar(40) NOT NULL,
  `stu_id` varchar(30) NOT NULL,
  `stu_name` varchar(30) NOT NULL,
  `term` varchar(30) NOT NULL,
  `course_name` varchar(60) NOT NULL,
  `course_nature` varchar(30) DEFAULT NULL,
  `course_credit` varchar(30) DEFAULT NULL,
  `course_time` varchar(30) DEFAULT NULL,
  `score` varchar(30) NOT NULL,
  `crawl_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for student_info
-- ----------------------------
DROP TABLE IF EXISTS `student_info`;
CREATE TABLE `student_info` (
  `id` varchar(40) NOT NULL,
  `stu_id` varchar(30) NOT NULL,
  `stu_name` varchar(30) NOT NULL,
  `class_name` varchar(30) NOT NULL,
  `term` varchar(30) NOT NULL,
  `fail_nums` varchar(10) DEFAULT NULL,
  `avg_nums` varchar(10) DEFAULT NULL,
  `credit_nums` varchar(10) DEFAULT NULL,
  `avg_credit_nums` varchar(10) DEFAULT NULL,
  `avg_credit_point_nums` varchar(10) DEFAULT NULL,
  `term_rank` varchar(10) DEFAULT NULL,
  `crawl_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
