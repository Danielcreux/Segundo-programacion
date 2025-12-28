<?php
/**
 * templates/customers.php
 *
 * Custom insert/update form for `customers` table.
 * Variables disponibles desde el microERP:
 * - $tabla
 * - $columnMeta
 * - $foreignKeys
 * - $primaryKey
 * - $conexion
 * - $template_mode  ('insert' | 'update')
 * - $fila_actual    (array con la fila en update, null en insert)
 * - $form_action    (URL para el <form action="...">)
 */

$is_update = isset($template_mode) && $template_mode === 'update';

// Para INSERT: priorizar lo que haya en $_POST (por si el insert falla por cualquier motivo).
// Para UPDATE: usar siempre los valores de $fila_actual (que ya vienen de la BD).
if ($is_update) {
    $email             = $fila_actual['email']            ?? '';
    $password_hash     = $fila_actual['password_hash']    ?? '';
    $first_name        = $fila_actual['first_name']       ?? '';
    $last_name         = $fila_actual['last_name']        ?? '';
    $phone             = $fila_actual['phone']            ?? '';
    $date_of_birth     = $fila_actual['date_of_birth']    ?? '';
    $registration_date = $fila_actual['registration_date']?? '';
    $last_login        = $fila_actual['last_login']       ?? '';
    $is_active_val     = $fila_actual['is_active']        ?? 1;
} else {
    $email             = $_POST['email']          ?? '';
    $password_hash     = $_POST['password_hash']  ?? '';
    $first_name        = $_POST['first_name']     ?? '';
    $last_name         = $_POST['last_name']      ?? '';
    $phone             = $_POST['phone']          ?? '';
    $date_of_birth     = $_POST['date_of_birth']  ?? '';
    $registration_date = '';  // lo gestiona la BD
    $last_login        = '';  // opcional, normalmente también la BD
    $is_active_val     = isset($_POST['is_active']) ? 1 : 1; // por defecto activo
}

$is_active_checked = ($is_active_val == 1 || $is_active_val === '1') ? 'checked' : '';
?>

<form action="<?php echo htmlspecialchars($form_action, ENT_QUOTES); ?>" method="POST">

  <!-- BLOQUE 1: Datos de acceso -->
  <div style="break-inside: avoid;">
    <h3 style="margin-top:0;color:indigo;font-size:14px;">Datos de acceso</h3>

    <label>Email</label>
    <input
      type="email"
      name="email"
      placeholder="email@dominio.com"
      value="<?php echo htmlspecialchars($email, ENT_QUOTES); ?>"
      required
    >

    <label>Contraseña (hash o valor que uses)</label>
    <input
      type="password"
      name="password_hash"
      placeholder="Password / Hash"
      value="<?php echo htmlspecialchars($password_hash, ENT_QUOTES); ?>"
      <?php echo $is_update ? '' : 'required'; ?>
    >
    <p style="font-size:11px;color:#666;margin-top:-6px;margin-bottom:12px;">
      Este campo se guarda en la columna <code>password_hash</code>.  
      Si quieres hashes reales, la lógica de hash debe hacerse en el script principal.
    </p>
  </div>

  <!-- BLOQUE 2: Datos personales -->
  <div style="break-inside: avoid;">
    <h3 style="margin-top:0;color:indigo;font-size:14px;">Datos personales</h3>

    <label>Nombre</label>
    <input
      type="text"
      name="first_name"
      placeholder="Nombre"
      value="<?php echo htmlspecialchars($first_name, ENT_QUOTES); ?>"
      required
    >

    <label>Apellidos</label>
    <input
      type="text"
      name="last_name"
      placeholder="Apellidos"
      value="<?php echo htmlspecialchars($last_name, ENT_QUOTES); ?>"
      required
    >

    <label>Teléfono</label>
    <input
      type="text"
      name="phone"
      placeholder="Teléfono"
      value="<?php echo htmlspecialchars($phone, ENT_QUOTES); ?>"
    >

    <label>Fecha de nacimiento</label>
    <input
      type="date"
      name="date_of_birth"
      value="<?php echo htmlspecialchars($date_of_birth, ENT_QUOTES); ?>"
    >
  </div>

  <!-- BLOQUE 3: Estado y metadatos -->
  <div style="break-inside: avoid;">
    <h3 style="margin-top:0;color:indigo;font-size:14px;">Estado y registro</h3>

    <label style="display:flex;align-items:center;gap:8px;margin-top:4px;">
      <input type="checkbox" name="is_active" value="1" <?php echo $is_active_checked; ?>>
      <span>Cliente activo</span>
    </label>
    <p style="font-size:11px;color:#666;margin-top:2px;">
      Se guarda en la columna <code>is_active</code> (BOOLEAN / TINYINT(1)).
    </p>

    <?php if ($is_update): ?>
      <div style="margin-top:10px;font-size:12px;color:#555;background:#f5f5ff;border-radius:8px;padding:8px 10px;">
        <div><strong>Fecha de alta:</strong>
          <?php echo $registration_date ? htmlspecialchars($registration_date, ENT_QUOTES) : '—'; ?>
        </div>
        <div><strong>Último acceso:</strong>
          <?php echo $last_login ? htmlspecialchars($last_login, ENT_QUOTES) : '—'; ?>
        </div>
        <p style="font-size:11px;color:#777;margin-top:6px;margin-bottom:0;">
          Estos campos (<code>registration_date</code>, <code>last_login</code>) se muestran sólo a modo informativo
          y no se editan desde este formulario.
        </p>
      </div>
    <?php else: ?>
      <p style="font-size:11px;color:#777;margin-top:10px;">
        La fecha de registro (<code>registration_date</code>) se establecerá automáticamente
        mediante el <code>DEFAULT CURRENT_TIMESTAMP</code> de la base de datos.
      </p>
    <?php endif; ?>
  </div>

  <!-- BOTÓN SUBMIT -->
  <div style="break-inside: avoid;">
    <input
      type="submit"
      value="<?php echo $is_update ? 'Guardar cambios' : 'Crear cliente'; ?>"
    >
  </div>

</form>

