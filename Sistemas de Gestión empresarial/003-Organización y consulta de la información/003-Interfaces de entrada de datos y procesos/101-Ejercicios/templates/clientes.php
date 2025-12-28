<?php
/**
 * templates/clientes.php
 *
 * Formulario personalizado para INSERT/UPDATE en la tabla `clientes`.
 *
 * Variables disponibles:
 * - $tabla
 * - $columnMeta
 * - $foreignKeys
 * - $primaryKey
 * - $conexion
 * - $template_mode  ('insert' | 'update')
 * - $fila_actual    (array en update, null en insert)
 * - $form_action    (URL para el <form action="...">)
 */

$is_update = isset($template_mode) && $template_mode === 'update';

// Valores para el formulario
if ($is_update) {
    $id_cliente      = $fila_actual['id_cliente']      ?? '';
    $email           = $fila_actual['email']           ?? '';
    $hash_contrasena = $fila_actual['hash_contrasena'] ?? '';
    $nombre          = $fila_actual['nombre']          ?? '';
    $apellido        = $fila_actual['apellido']        ?? '';
    $telefono        = $fila_actual['telefono']        ?? '';
    $fecha_nacimiento= $fila_actual['fecha_nacimiento']?? '';
    $fecha_registro  = $fila_actual['fecha_registro']  ?? '';
    $ultimo_acceso   = $fila_actual['ultimo_acceso']   ?? '';
    $esta_activo_val = $fila_actual['esta_activo']     ?? 1;
} else {
    $id_cliente      = '';
    $email           = $_POST['email']           ?? '';
    $hash_contrasena = $_POST['hash_contrasena'] ?? '';
    $nombre          = $_POST['nombre']          ?? '';
    $apellido        = $_POST['apellido']        ?? '';
    $telefono        = $_POST['telefono']        ?? '';
    $fecha_nacimiento= $_POST['fecha_nacimiento']?? '';
    $fecha_registro  = '';  // lo controla la BD
    $ultimo_acceso   = '';  // típicamente también la BD
    $esta_activo_val = isset($_POST['esta_activo']) ? 1 : 1; // por defecto activo
}

$esta_activo_checked = ($esta_activo_val == 1 || $esta_activo_val === '1') ? 'checked' : '';
?>

<style>
/* Layout propio para este formulario, sobreescribe el columns:2 global */
form.form-template-clientes{
  columns:1 !important;
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:20px;
}

/* Tarjetas de sección */
.form-template-clientes .clientes-block{
  background: radial-gradient(circle at 0 0, rgba(255,255,255,0.9), #f4f3ff);
  border-radius:var(--radio,10px);
  border:1px solid rgba(75,0,130,0.15);
  padding:18px 20px;
  box-shadow:0 8px 24px rgba(0,0,0,0.08);
  position:relative;
  overflow:hidden;
  break-inside:avoid;
}

/* Detalle decorativo en la esquina */
.form-template-clientes .clientes-block::before{
  content:"";
  position:absolute;
  width:90px;
  height:90px;
  border-radius:50%;
  background:radial-gradient(circle, rgba(75,0,130,0.18), transparent 70%);
  top:-40px;
  right:-20px;
  opacity:0.9;
}

.form-template-clientes .clientes-block h3{
  margin-top:0;
  margin-bottom:6px;
  font-size:15px;
  color:var(--color_primario,indigo);
  position:relative;
  z-index:1;
}

.form-template-clientes .clientes-block small{
  display:block;
  font-size:11px;
  color:#777;
  margin-bottom:10px;
  position:relative;
  z-index:1;
}

/* Campos */
.form-template-clientes label{
  display:block;
  font-weight:600;
  margin-bottom:4px;
  font-size:12px;
  color:#444;
  position:relative;
  z-index:1;
}

.form-template-clientes input,
.form-template-clientes textarea{
  width:100%;
  padding:9px 11px;
  margin-bottom:10px;
  border:1px solid rgba(75,0,130,0.28);
  border-radius:8px;
  font-size:13px;
  background-color:#ffffff;
  box-sizing:border-box;
  position:relative;
  z-index:1;
}

.form-template-clientes textarea{
  min-height:70px;
  resize:vertical;
}

.form-template-clientes input:focus,
.form-template-clientes textarea:focus{
  outline:none;
  border-color:var(--color_primario,indigo);
  box-shadow:0 0 0 2px rgba(75,0,130,0.18);
}

/* Checkbox activo */
.form-template-clientes .checkbox-row{
  display:flex;
  align-items:center;
  gap:8px;
  margin-top:4px;
  position:relative;
  z-index:1;
}
.form-template-clientes .checkbox-row input[type=checkbox]{
  width:auto;
  margin-bottom:0;
  box-shadow:none;
}

/* Footer botones */
.form-template-clientes .clientes-footer{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap:12px;
  position:relative;
  z-index:1;
}

.form-template-clientes .clientes-footer input[type=submit]{
  background:linear-gradient(135deg, var(--color_primario,indigo), #9b59b6);
  color:white;
  cursor:pointer;
  border:none;
  font-weight:600;
  text-transform:uppercase;
  letter-spacing:0.8px;
  box-shadow:0 4px 12px rgba(75,0,130,0.5);
  padding:10px 20px;
  border-radius:999px;
}

.form-template-clientes .clientes-footer input[type=submit]:hover{
  box-shadow:0 6px 18px rgba(75,0,130,0.7);
  transform:translateY(-1px);
}
</style>

<form action="<?php echo htmlspecialchars($form_action, ENT_QUOTES); ?>" method="POST" class="form-template-clientes">

  <!-- BLOQUE 1: Identificación y acceso -->
  <div class="clientes-block">
    <h3>Identificación &amp; acceso</h3>
    <small>Datos básicos del cliente y credenciales.</small>

    <?php if ($is_update && $id_cliente !== ''): ?>
      <label>ID cliente</label>
      <input type="text" value="<?php echo htmlspecialchars($id_cliente, ENT_QUOTES); ?>" disabled>
    <?php endif; ?>

    <label>Email</label>
    <input
      type="email"
      name="email"
      placeholder="cliente@dominio.com"
      value="<?php echo htmlspecialchars($email, ENT_QUOTES); ?>"
      required
    >

    <label>Contraseña (hash)</label>
    <input
      type="password"
      name="hash_contrasena"
      placeholder="Contraseña / hash"
      value="<?php echo htmlspecialchars($hash_contrasena, ENT_QUOTES); ?>"
      <?php echo $is_update ? '' : 'required'; ?>
    >
    <small>
      Se guarda en la columna <code>hash_contrasena</code>.
      El cálculo del hash debe realizarse en la lógica del servidor principal.
    </small>
  </div>

  <!-- BLOQUE 2: Datos personales -->
  <div class="clientes-block">
    <h3>Datos personales</h3>
    <small>Información básica para identificar al cliente.</small>

    <label>Nombre</label>
    <input
      type="text"
      name="nombre"
      placeholder="Nombre"
      value="<?php echo htmlspecialchars($nombre, ENT_QUOTES); ?>"
      required
    >

    <label>Apellido</label>
    <input
      type="text"
      name="apellido"
      placeholder="Apellido"
      value="<?php echo htmlspecialchars($apellido, ENT_QUOTES); ?>"
      required
    >

    <label>Teléfono</label>
    <input
      type="text"
      name="telefono"
      placeholder="Teléfono"
      value="<?php echo htmlspecialchars($telefono, ENT_QUOTES); ?>"
    >

    <label>Fecha de nacimiento</label>
    <input
      type="date"
      name="fecha_nacimiento"
      value="<?php echo htmlspecialchars($fecha_nacimiento, ENT_QUOTES); ?>"
    >
  </div>

  <!-- BLOQUE 3: Estado y actividad -->
  <div class="clientes-block">
    <h3>Estado &amp; actividad</h3>
    <small>Control de alta, último acceso y si el cliente está activo.</small>

    <div class="checkbox-row">
      <input type="checkbox" name="esta_activo" value="1" <?php echo $esta_activo_checked; ?>>
      <span>Cliente activo</span>
    </div>
    <small>
      Se almacena en la columna <code>esta_activo</code> (BOOLEAN / TINYINT(1)).
    </small>

    <?php if ($is_update): ?>
      <div style="margin-top:12px;font-size:12px;color:#555;background:#f6f4ff;border-radius:8px;padding:8px 10px;">
        <div><strong>Fecha de registro:</strong>
          <?php echo $fecha_registro ? htmlspecialchars($fecha_registro, ENT_QUOTES) : '—'; ?>
        </div>
        <div><strong>Último acceso:</strong>
          <?php echo $ultimo_acceso ? htmlspecialchars($ultimo_acceso, ENT_QUOTES) : '—'; ?>
        </div>
        <p style="font-size:11px;color:#777;margin-top:6px;margin-bottom:0;">
          Estos campos (<code>fecha_registro</code>, <code>ultimo_acceso</code>) son informativos y no se editan desde este formulario.
        </p>
      </div>
    <?php else: ?>
      <small style="display:block;margin-top:10px;">
        La fecha de registro (<code>fecha_registro</code>) se asignará automáticamente
        mediante <code>DEFAULT CURRENT_TIMESTAMP</code>.
      </small>
    <?php endif; ?>
  </div>

  <!-- BLOQUE 4: Botón -->
  <div class="clientes-block clientes-footer">
    <input
      type="submit"
      value="<?php echo $is_update ? 'Guardar cambios' : 'Crear cliente'; ?>"
    >
  </div>

</form>

