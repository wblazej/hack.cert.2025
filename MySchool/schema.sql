DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(9) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(100),
  `bio` varchar(255),
  `session_id` varchar(100),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=ASCII;

INSERT INTO `users` (`id`, `username`, `bio`) VALUES (1, 'test', 'test bio');
