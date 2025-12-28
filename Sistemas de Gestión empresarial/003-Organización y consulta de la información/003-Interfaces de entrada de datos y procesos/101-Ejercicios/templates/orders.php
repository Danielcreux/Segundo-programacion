<?php
/**
 * templates/orders.php
 *
 * Custom insert/update form for `orders` table.
 * Variables disponibles desde el microERP:
 * - $tabla
 * - $columnMeta
 * - $foreignKeys
 * - $primaryKey
 * - $conexion
 * - $template_mode  ('insert' | 'update')
 * - $fila_actual    (array con la fila en update, null en insert)
 * - $form_action    (URL para el <form action="...">)
 * - $db_name        (nombre de la BD)
 */

$is_update = isset($template_mode) && $template_mode === 'update';

if ($is_update) {
    $order_id            = $fila_actual['order_id']             ?? '';
    $customer_id         = $fila_actual['customer_id']          ?? '';
    $order_number        = $fila_actual['order_number']         ?? '';
    $order_date          = $fila_actual['order_date']           ?? '';
    $status_id           = $fila_actual['status_id']            ?? '';
    $payment_status_id   = $fila_actual['payment_status_id']    ?? '';
    $payment_method_id   = $fila_actual['payment_method_id']    ?? '';
    $shipping_method_id  = $fila_actual['shipping_method_id']   ?? '';
    $shipping_address_id = $fila_actual['shipping_address_id']  ?? '';
    $billing_address_id  = $fila_actual['billing_address_id']   ?? '';
    $subtotal            = $fila_actual['subtotal']             ?? '';
    $tax_amount          = $fila_actual['tax_amount']           ?? '';
    $shipping_cost       = $fila_actual['shipping_cost']        ?? '';
    $discount_amount     = $fila_actual['discount_amount']      ?? '';
    $total_amount        = $fila_actual['total_amount']         ?? '';
    $notes               = $fila_actual['notes']                ?? '';
} else {
    $order_id            = '';
    $customer_id         = $_POST['customer_id']         ?? '';
    $order_number        = $_POST['order_number']        ?? '';
    $order_date          = ''; // lo pone la BD por defecto
    $status_id           = $_POST['status_id']           ?? '';
    $payment_status_id   = $_POST['payment_status_id']   ?? '';
    $payment_method_id   = $_POST['payment_method_id']   ?? '';
    $shipping_method_id  = $_POST['shipping_method_id']  ?? '';
    $shipping_address_id = $_POST['shipping_address_id'] ?? '';
    $billing_address_id  = $_POST['billing_address_id']  ?? '';
    $subtotal            = $_POST['subtotal']            ?? '';
    $tax_amount          = $_POST['tax_amount']          ?? '';
    $shipping_cost       = $_POST['shipping_cost']       ?? '';
    $discount_amount     = $_POST['discount_amount']     ?? '0.00';
    $total_amount        = $_POST['total_amount']        ?? '';
    $notes               = $_POST['notes']               ?? '';
}

/**
 * Helper: obtener opciones de un campo FK como [ ['value'=>..., 'label'=>...], ... ]
 */
$getOptionsForFk = function(string $fk_column) use ($foreignKeys, $conexion) {
    if (!isset($foreignKeys[$fk_column])) {
        return [];
    }
    $fk_info    = $foreignKeys[$fk_column];
    $tabla_fk   = $fk_info['tabla'];
    $columna_fk = $fk_info['columna'];

    $opts = [];
    $sql  = "SELECT * FROM ".$tabla_fk." ORDER BY ".$columna_fk." ASC";
    $res  = mysqli_query($conexion, $sql);
    if ($res) {
        while($row = mysqli_fetch_assoc($res)){
            $label_parts = [];
            foreach($row as $k=>$v){
                $label_parts[] = $v;
            }
            $opts[] = [
                'value' => $row[$columna_fk],
                'label' => implode(" | ", $label_parts)
            ];
        }
    }
    return $opts;
};

$options_customers        = $getOptionsForFk('customer_id');
$options_statuses         = $getOptionsForFk('status_id');
$options_payment_statuses = $getOptionsForFk('payment_status_id');
$options_payment_methods  = $getOptionsForFk('payment_method_id');
$options_shipping_methods = $getOptionsForFk('shipping_method_id');
$options_addresses        = $getOptionsForFk('shipping_address_id'); // mismo FK para shipping/billing
?>

<style>
/* Override layout from global form (columns:2) for this template */
form.form-template-orders{
  columns:1 !important;
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:20px;
}

/* “Tarjetas” para cada bloque de datos */
.form-template-orders .orders-block{
  background:#ffffff;
  border-radius:var(--radio,8px);
  border:1px solid rgba(75,0,130,0.18);
  padding:16px 18px;
  box-shadow:0 4px 14px rgba(0,0,0,0.06);
  break-inside:avoid;
}

.form-template-orders .orders-block h3{
  margin-top:0;
  margin-bottom:8px;
  font-size:14px;
  color:var(--color_primario,indigo);
}

.form-template-orders .orders-block small{
  display:block;
  font-size:11px;
  color:#777;
  margin-bottom:8px;
}

.form-template-orders label{
  display:block;
  font-weight:600;
  margin-bottom:4px;
  font-size:12px;
  color:#444;
}

.form-template-orders input,
.form-template-orders select,
.form-template-orders textarea{
  width:100%;
  padding:8px 10px;
  margin-bottom:10px;
  border:1px solid rgba(75,0,130,0.3);
  border-radius:var(--radio,8px);
  font-size:13px;
  background-color:#fff;
  box-sizing:border-box;
}

.form-template-orders textarea{
  min-height:80px;
  resize:vertical;
}

.form-template-orders input:focus,
.form-template-orders select:focus,
.form-template-orders textarea:focus{
  outline:none;
  border-color:var(--color_primario,indigo);
  box-shadow:0 0 0 2px rgba(75,0,130,0.15);
}

.form-template-orders .orders-footer{
  display:flex;
  align-items:center;
  justify-content:flex-end;
}

.form-template-orders .orders-footer input[type=submit]{
  background-color:var(--color_primario,indigo);
  color:white;
  cursor:pointer;
  border:none;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:0.8px;
  box-shadow:0 4px 10px rgba(75,0,130,0.4);
  padding:10px 18px;
}
</style>

<form action="<?php echo htmlspecialchars($form_action, ENT_QUOTES); ?>" method="POST" class="form-template-orders">

  <!-- BLOQUE: Info pedido y cliente -->
  <div class="orders-block">
    <h3>Pedido &amp; Cliente</h3>
    <small>Datos básicos del pedido y a quién pertenece.</small>

    <?php if ($is_update && $order_id !== ''): ?>
      <label>ID Pedido</label>
      <input type="text" value="<?php echo htmlspecialchars($order_id, ENT_QUOTES); ?>" disabled>
    <?php endif; ?>

    <label>Cliente</label>
    <select name="customer_id" required>
      <option value="">— seleccionar cliente —</option>
      <?php foreach($options_customers as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $customer_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Número de pedido</label>
    <input
      type="text"
      name="order_number"
      placeholder="Ej: ORD-2025-0001"
      value="<?php echo htmlspecialchars($order_number, ENT_QUOTES); ?>"
      required
    >

    <?php if ($is_update): ?>
      <label>Fecha de pedido</label>
      <input
        type="text"
        value="<?php echo $order_date ? htmlspecialchars($order_date, ENT_QUOTES) : '—'; ?>"
        disabled
      >
      <small>La fecha se establece automáticamente mediante <code>DEFAULT CURRENT_TIMESTAMP</code>.</small>
    <?php else: ?>
      <small>La fecha del pedido se establecerá automáticamente al crear el registro.</small>
    <?php endif; ?>
  </div>

  <!-- BLOQUE: Estado & pago -->
  <div class="orders-block">
    <h3>Estado &amp; Pago</h3>
    <small>Estado del pedido, pago y método de pago.</small>

    <label>Estado del pedido</label>
    <select name="status_id" required>
      <option value="">— seleccionar estado —</option>
      <?php foreach($options_statuses as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $status_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Estado del pago</label>
    <select name="payment_status_id" required>
      <option value="">— seleccionar estado de pago —</option>
      <?php foreach($options_payment_statuses as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $payment_status_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Método de pago</label>
    <select name="payment_method_id" required>
      <option value="">— seleccionar método de pago —</option>
      <?php foreach($options_payment_methods as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $payment_method_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>
  </div>

  <!-- BLOQUE: Envío & direcciones -->
  <div class="orders-block">
    <h3>Envío &amp; Direcciones</h3>
    <small>Método de envío y direcciones de entrega y facturación.</small>

    <label>Método de envío</label>
    <select name="shipping_method_id" required>
      <option value="">— seleccionar método de envío —</option>
      <?php foreach($options_shipping_methods as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $shipping_method_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Dirección de envío</label>
    <select name="shipping_address_id" required>
      <option value="">— seleccionar dirección de envío —</option>
      <?php foreach($options_addresses as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $shipping_address_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>

    <label>Dirección de facturación</label>
    <select name="billing_address_id" required>
      <option value="">— seleccionar dirección de facturación —</option>
      <?php foreach($options_addresses as $opt): ?>
        <option value="<?php echo htmlspecialchars($opt['value'],ENT_QUOTES); ?>"
          <?php echo ($opt['value'] == $billing_address_id ? 'selected' : ''); ?>>
          <?php echo htmlspecialchars($opt['label'],ENT_QUOTES); ?>
        </option>
      <?php endforeach; ?>
    </select>
  </div>

  <!-- BLOQUE: Totales -->
  <div class="orders-block">
    <h3>Totales</h3>
    <small>Importes económicos asociados al pedido.</small>

    <label>Subtotal</label>
    <input
      type="number"
      name="subtotal"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($subtotal, ENT_QUOTES); ?>"
      required
    >

    <label>Impuestos</label>
    <input
      type="number"
      name="tax_amount"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($tax_amount, ENT_QUOTES); ?>"
      required
    >

    <label>Coste de envío</label>
    <input
      type="number"
      name="shipping_cost"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($shipping_cost, ENT_QUOTES); ?>"
      required
    >

    <label>Descuento</label>
    <input
      type="number"
      name="discount_amount"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($discount_amount, ENT_QUOTES); ?>"
    >

    <label>Total</label>
    <input
      type="number"
      name="total_amount"
      step="0.01"
      min="0"
      value="<?php echo htmlspecialchars($total_amount, ENT_QUOTES); ?>"
      required
    >
    <small>
      Puedes calcular el total en tu lógica de negocio
      (por ejemplo, subtotal + impuestos + envío − descuento) y sólo mostrarlo aquí
      o permitir editarlo manualmente.
    </small>
  </div>

  <!-- BLOQUE: Notas -->
  <div class="orders-block">
    <h3>Notas internas</h3>
    <small>Información adicional sobre el pedido.</small>

    <label>Notas</label>
    <textarea
      name="notes"
      placeholder="Observaciones, comentarios del cliente, notas internas..."
    ><?php echo htmlspecialchars($notes, ENT_QUOTES); ?></textarea>
  </div>

  <!-- BOTÓN SUBMIT -->
  <div class="orders-block orders-footer">
    <input
      type="submit"
      value="<?php echo $is_update ? 'Guardar cambios' : 'Crear pedido'; ?>"
    >
  </div>

</form>

