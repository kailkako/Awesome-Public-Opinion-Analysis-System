/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50519
 Source Host           : localhost:3306
 Source Schema         : weiboarticles

 Target Server Type    : MySQL
 Target Server Version : 50519
 File Encoding         : 65001

 Date: 21/09/2024 21:29:12
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for article
-- ----------------------------
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article`  (
  `id` bigint(20) NULL DEFAULT NULL,
  `likeNum` bigint(20) NULL DEFAULT NULL,
  `commentsLen` bigint(20) NULL DEFAULT NULL,
  `reposts_count` bigint(20) NULL DEFAULT NULL,
  `region` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `detailUrl` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorName` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorDetail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `negative_ratio` float NULL DEFAULT NULL,
  `positive_ratio` float NULL DEFAULT NULL,
  `emotion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for article_temp
-- ----------------------------
DROP TABLE IF EXISTS `article_temp`;
CREATE TABLE `article_temp`  (
  `id` bigint(20) NULL DEFAULT NULL,
  `likeNum` bigint(20) NULL DEFAULT NULL,
  `commentsLen` bigint(20) NULL DEFAULT NULL,
  `reposts_count` bigint(20) NULL DEFAULT NULL,
  `region` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `type` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `detailUrl` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorName` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorDetail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `negative_ratio` float NULL DEFAULT NULL,
  `positive_ratio` float NULL DEFAULT NULL,
  `emotion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for comments
-- ----------------------------
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments`  (
  `articleId` bigint(20) NULL DEFAULT NULL,
  `created_at` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `likes_counts` bigint(20) NULL DEFAULT NULL,
  `region` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorName` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorGender` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorAddress` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `sentiment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for comments_temp
-- ----------------------------
DROP TABLE IF EXISTS `comments_temp`;
CREATE TABLE `comments_temp`  (
  `articleId` bigint(20) NULL DEFAULT NULL,
  `created_at` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `likes_counts` bigint(20) NULL DEFAULT NULL,
  `region` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorName` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorGender` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `authorAddress` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `sentiment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `createTime` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
