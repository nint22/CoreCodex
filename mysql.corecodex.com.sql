-- phpMyAdmin SQL Dump
-- version 3.3.7
-- http://www.phpmyadmin.net
--
-- Host: mysql.corecodex.com
-- Generation Time: Feb 09, 2011 at 07:27 PM
-- Server version: 5.1.53
-- PHP Version: 5.2.15

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `corecodexdb`
--
CREATE DATABASE `corecodexdb` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `corecodexdb`;

-- --------------------------------------------------------

--
-- Table structure for table `Achievements`
--

CREATE TABLE IF NOT EXISTS `Achievements` (
  `AchievementID` int(11) NOT NULL,
  `AchievementIconFileLocation` varchar(1024) NOT NULL,
  `AchievementName` varchar(128) NOT NULL,
  `AchievementDescription` varchar(1024) NOT NULL,
  `AchievementScore` int(11) NOT NULL,
  KEY `AchievementID` (`AchievementID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `Achievements`
--

INSERT INTO `Achievements` (`AchievementID`, `AchievementIconFileLocation`, `AchievementName`, `AchievementDescription`, `AchievementScore`) VALUES
(3, 'images/achievement3.png', 'Late Bloomer', 'Solve a challenge with a run time within 90%+ of the maximum time', 5),
(2, 'images/achievement2.png', 'Speed Daemon', 'Solve a challenge within 10% of the maximum time', 10),
(1, 'images/achievement1.png', 'Beta Get In Here', 'Create an account during CoreCodex beta testing', 5),
(0, 'images/achievement0.png', 'Alpha Pack Leader', 'Create an account during CoreCodex alpha testing', 5),
(4, 'images/achievement4.png', 'Baby Steps', 'Solve at least one challenge', 5),
(5, 'images/achievement5.png', 'Think Fast', 'Have your solution be accepted on the first attempt', 15),
(6, 'images/achievement6.png', 'Revenge!', 'Break the judging system', 50),
(7, 'images/achievement7.png', 'Practice Badge', 'Obtain a user score of over 5 points', 5),
(8, 'images/achievement8.png', 'Copper Badge', 'Obtain a user score of over 15 points', 10),
(9, 'images/achievement9.png', 'Bronze Badge', 'Obtain a user score of over 50 points', 10),
(10, 'images/achievement10.png', 'Silver Badge', 'Obtain a user score of over 100 points', 10),
(11, 'images/achievement11.png', 'Gold Badge', 'Obtain a user score of over 150 points', 10),
(12, 'images/achievement12.png', 'Platinum Badge', 'Obtain a user score of over 200 points', 10),
(13, 'images/achievement13.png', 'Pro Badge', 'Obtain a user score of over 250 points', 50),
(14, 'images/achievement14.png', 'The Architect', 'Be a CoreCodex developer', 100),
(15, 'images/achievement15.png', 'Adminium', 'Be an administrator', 25),
(16, 'images/achievement16.png', 'Tripoli Win', 'Solve three problems consecutively', 20),
(16, 'images/achievement16.png', 'What standards?', 'Access the site using an Internet Explorer browser', 5),
(17, 'images/achievement17.png', 'Forever Alone', 'Fail three consecutive problems', 5),
(18, 'images/achievement18.png', 'I Accidentally The Whole Thing', 'Submit code that does not compile', 5),
(19, 'images/achievement19.png', 'Game Master', 'Submit a programming challenge', 10),
(20, 'images/achievement20.png', 'The Knuth', 'Cause a run-time bug. "Beware of bugs in the above code; I have only proved it correct, not tried it."', 5);

-- --------------------------------------------------------

--
-- Table structure for table `ChallengeDescriptions`
--

CREATE TABLE IF NOT EXISTS `ChallengeDescriptions` (
  `ChallengeID` int(11) NOT NULL AUTO_INCREMENT,
  `ChallengeGroupID` int(11) NOT NULL,
  `XMLFileLocation` varchar(1024) NOT NULL,
  PRIMARY KEY (`ChallengeID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=12 ;

--
-- Dumping data for table `ChallengeDescriptions`
--

INSERT INTO `ChallengeDescriptions` (`ChallengeID`, `ChallengeGroupID`, `XMLFileLocation`) VALUES
(1, 1, 'challenges/python0_0.xml'),
(2, 1, 'challenges/python0_1.xml'),
(3, 1, 'challenges/python0_2.xml'),
(4, 1, 'challenges/python0_3.xml'),
(5, 1, 'challenges/python0_4.xml'),
(6, 1, 'challenges/python0_5.xml'),
(7, 2, 'challenges/beta_1.xml'),
(8, 2, 'challenges/beta_0.xml'),
(9, 3, 'challenges/alpha_2.xml'),
(10, 3, 'challenges/alpha_1.xml'),
(11, 3, 'challenges/alpha_0.xml');

-- --------------------------------------------------------

--
-- Table structure for table `ChallengeGroups`
--

CREATE TABLE IF NOT EXISTS `ChallengeGroups` (
  `ChallengeGroupID` int(11) NOT NULL AUTO_INCREMENT,
  `ChallengeGroupName` varchar(128) NOT NULL,
  `ChallengeGroupDescription` longtext NOT NULL,
  PRIMARY KEY (`ChallengeGroupID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6 ;

--
-- Dumping data for table `ChallengeGroups`
--

INSERT INTO `ChallengeGroups` (`ChallengeGroupID`, `ChallengeGroupName`, `ChallengeGroupDescription`) VALUES
(1, 'Python Programming Practice (1 of 3)', 'Practice your Python basics - focuses on standard output manipulation.'),
(2, 'Python Programming Practice (2 of 3)', 'Practice your Python basics - focuses on control structures.'),
(3, 'Python Programming Practice (3 of 3)', 'Practice your Python basics - combines control structures and conditionals.'),
(4, 'Python Strings', 'Exercise your string manipulation power in Python!'),
(5, 'Basic C Programming', 'Exercise your basic C programming skills.');

-- --------------------------------------------------------

--
-- Table structure for table `UserAchievements`
--

CREATE TABLE IF NOT EXISTS `UserAchievements` (
  `UserID` int(11) NOT NULL,
  `AchievementID` int(11) NOT NULL,
  KEY `UserID` (`UserID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `UserAchievements`
--

INSERT INTO `UserAchievements` (`UserID`, `AchievementID`) VALUES
(34, 0),
(20, 0),
(33, 0),
(4, 0),
(32, 0),
(31, 0),
(4, 14),
(30, 0),
(35, 0),
(38, 0),
(37, 0),
(36, 0),
(36, 6),
(39, 0),
(40, 0),
(41, 0),
(42, 0),
(39, 20),
(46, 0),
(47, 0),
(48, 0),
(49, 0);

-- --------------------------------------------------------

--
-- Table structure for table `UserSolutions`
--

CREATE TABLE IF NOT EXISTS `UserSolutions` (
  `SolutionID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) NOT NULL,
  `ChallengeID` int(11) NOT NULL,
  `ResultCode` int(11) NOT NULL,
  `ResultString` longtext NOT NULL,
  `MemoryUsage` int(11) NOT NULL,
  `RuntimeUsage` int(11) NOT NULL,
  `SourceCode` longtext NOT NULL,
  `SourceLanguage` varchar(32) NOT NULL,
  `SubmitDateTime` datetime NOT NULL,
  PRIMARY KEY (`SolutionID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `UserSolutions`
--

INSERT INTO `UserSolutions` (`SolutionID`, `UserID`, `ChallengeID`, `ResultCode`, `ResultString`, `MemoryUsage`, `RuntimeUsage`, `SourceCode`, `SourceLanguage`, `SubmitDateTime`) VALUES
(1, 4, 1, 0, '', 123, 321, 'def main():\r\n	print "Something..." # Write your code here...\r\n	', 'Python', '2011-02-09 21:44:40'),
(2, 4, 1, 1, '', 123, 321, 'def main():\r\n	print "Something..." # Write your code here...\r\n	', 'Python', '2011-02-09 21:45:42'),
(3, 4, 1, 0, 'Internal Failure', 8192, 3000, 'def main():\r\n	print "Something..." # Write your code here...\r\n	', 'Python', '2011-02-09 22:26:53');

-- --------------------------------------------------------

--
-- Table structure for table `Users`
--

CREATE TABLE IF NOT EXISTS `Users` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(64) NOT NULL,
  `UserEMail` varchar(64) NOT NULL,
  `UserPassword` varchar(64) NOT NULL,
  `LogInCount` int(11) NOT NULL,
  `LastLogin` datetime NOT NULL,
  `IsAdmin` tinyint(1) NOT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=50 ;

--
-- Dumping data for table `Users`
--

INSERT INTO `Users` (`UserID`, `UserName`, `UserEMail`, `UserPassword`, `LogInCount`, `LastLogin`, `IsAdmin`) VALUES
<REMOVED>
