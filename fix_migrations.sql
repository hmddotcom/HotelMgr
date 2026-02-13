-- Fix migration dependency conflict
-- Run this in phpMyAdmin or MySQL Workbench

USE hotelerie_db;

-- Delete settings migrations
DELETE FROM django_migrations WHERE app='settings';

-- Delete admin migrations that depend on settings
DELETE FROM django_migrations WHERE app='admin';

-- Delete contenttypes migrations
DELETE FROM django_migrations WHERE app='contenttypes' AND name='0002_remove_content_type_name';

-- Delete auth migrations that depend on contenttypes
DELETE FROM django_migrations WHERE app='auth' AND id > 1;
