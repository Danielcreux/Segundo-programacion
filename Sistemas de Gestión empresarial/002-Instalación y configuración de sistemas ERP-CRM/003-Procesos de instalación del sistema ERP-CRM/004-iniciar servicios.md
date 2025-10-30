sudo systemctl enable odoo
sudo systemctl start odoo
sudo systemctl status odoo

# Arreglo de librerias

sudo apt install python3-pip -y
sudo pip install lxml[html_clean] --break-system-packages

Arrancamos manualmente

dpkg -l | grep -i odoo
apt policy odoo
ls -l /etc/init.d/odoo || true
command -v odoo || ls -l /usr/bin/odoo* /usr/local/bin/odoo* 2>/dev/null || true

