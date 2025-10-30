sudo apt update
sudo apt install -y postgresql
sudo systemctl enable --now postgresql
sudo -u postgres createuser -s odoo || true
