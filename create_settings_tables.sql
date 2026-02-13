-- Create settings tables manually
USE hotelerie_db;

CREATE TABLE `settings_appsettings` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `hotel_name` varchar(100) NOT NULL, `contact_email` varchar(254) NOT NULL, `contact_phone` varchar(20) NOT NULL, `address` longtext NOT NULL, `currency` varchar(3) NOT NULL, `timezone` varchar(50) NOT NULL, `logo` varchar(100) NULL, `favicon` varchar(100) NULL, `primary_color` varchar(7) NOT NULL, `sidebar_color` varchar(7) NOT NULL);

CREATE TABLE `settings_role` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(50) NOT NULL UNIQUE, `description` longtext NOT NULL, `created_at` datetime(6) NOT NULL);

CREATE TABLE `settings_customuser` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `password` varchar(128) NOT NULL, `last_login` datetime(6) NULL, `is_superuser` bool NOT NULL, `username` varchar(150) NOT NULL UNIQUE, `first_name` varchar(150) NOT NULL, `last_name` varchar(150) NOT NULL, `email` varchar(254) NOT NULL, `is_staff` bool NOT NULL, `is_active` bool NOT NULL, `date_joined` datetime(6) NOT NULL, `phone` varchar(20) NOT NULL, `is_active_custom` bool NOT NULL, `role_id` bigint NULL);

CREATE TABLE `settings_customuser_groups` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `customuser_id` bigint NOT NULL, `group_id` integer NOT NULL);

CREATE TABLE `settings_customuser_user_permissions` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `customuser_id` bigint NOT NULL, `permission_id` integer NOT NULL);

CREATE TABLE `settings_permission` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `module` varchar(20) NOT NULL, `action` varchar(10) NOT NULL, `role_id` bigint NOT NULL);

ALTER TABLE `settings_customuser` ADD CONSTRAINT `settings_customuser_role_id_adad97f1_fk_settings_role_id` FOREIGN KEY (`role_id`) REFERENCES `settings_role` (`id`);
ALTER TABLE `settings_customuser_groups` ADD CONSTRAINT `settings_customuser_groups_customuser_id_group_id_6eca13c4_uniq` UNIQUE (`customuser_id`, `group_id`);
ALTER TABLE `settings_customuser_groups` ADD CONSTRAINT `settings_customuser__customuser_id_4bfca3c6_fk_settings_` FOREIGN KEY (`customuser_id`) REFERENCES `settings_customuser` (`id`);
ALTER TABLE `settings_customuser_groups` ADD CONSTRAINT `settings_customuser_groups_group_id_12816eb2_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);
ALTER TABLE `settings_customuser_user_permissions` ADD CONSTRAINT `settings_customuser_user_customuser_id_permission_11137655_uniq` UNIQUE (`customuser_id`, `permission_id`);
ALTER TABLE `settings_customuser_user_permissions` ADD CONSTRAINT `settings_customuser__customuser_id_ddbab59b_fk_settings_` FOREIGN KEY (`customuser_id`) REFERENCES `settings_customuser` (`id`);
ALTER TABLE `settings_customuser_user_permissions` ADD CONSTRAINT `settings_customuser__permission_id_bd0148bd_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`);
ALTER TABLE `settings_permission` ADD CONSTRAINT `settings_permission_role_id_module_action_00bc3a91_uniq` UNIQUE (`role_id`, `module`, `action`);
ALTER TABLE `settings_permission` ADD CONSTRAINT `settings_permission_role_id_0a5fd9d2_fk_settings_role_id` FOREIGN KEY (`role_id`) REFERENCES `settings_role` (`id`);

-- Mark migration as applied
INSERT INTO django_migrations (app, name, applied) VALUES ('settings', '0001_initial', NOW());
