sudo nano /opt/odoo/custom-addons/mi_modulo_ejemplo/security/ir.model.access.csv


id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_nota_public,access_nota_public,model_mi_modulo_ejemplo_nota,base.group_user,1,1,1,1

Actualizamos desde consola

sudo -u odoo /usr/bin/odoo -d odoo --update=mi_modulo_ejemplo --stop-after-init

Reiniciamos odoo
sudo systemctl restart odoo || sudo service odoo restart

sudo -u odoo /usr/bin/odoo -d dam1 --update=mi_modulo_ejemplo --stop-after-init

id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_mi_modulo_ejemplo_user,mi.modulo.ejemplo.user,model_mi_modulo_ejemplo,base.group_user,1,1,1,0
access_mi_modulo_ejemplo_manager,mi.modulo.ejemplo.manager,model_mi_modulo_ejemplo,base.group_system,1,1,1,1