sudo mysql -u root -p

CREATE DATABASE accesoadatos2526;

CREATE USER 
'accesoadatos2526'@'localhost' 
IDENTIFIED BY 'Accesoadatos2526$';

GRANT USAGE ON *.* TO 'accesoadatos2526'@'localhost';

ALTER USER 'accesoadatos2526'@'localhost' 
REQUIRE NONE 
WITH MAX_QUERIES_PER_HOUR 0 
MAX_CONNECTIONS_PER_HOUR 0 
MAX_UPDATES_PER_HOUR 0 
MAX_USER_CONNECTIONS 0;

GRANT ALL PRIVILEGES ON `accesoadatos2526`.* 
TO 'accesoadatos2526'@'localhost';

