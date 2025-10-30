sudo nano /etc/odoo/odoo.conf

addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons

Control+O = Guardar
Control+X = Salir

Reiniciamos odoo
sudo systemctl restart odoo
systemctl daemon-reload

Actualizar aplicaciones (boton en la barra superior)

