<?php

class JVDB {
    private $host;
    private $usuario;
    private $contrasena;
    private $basedatos;
    private $conexion;

    public function __construct($host, $usuario, $contrasena, $basedatos) {
        $this->host = $host;
        $this->usuario = $usuario;
        $this->contrasena = $contrasena;
        $this->basedatos = $basedatos;

        $this->conexion = new mysqli($this->host, $this->usuario, $this->contrasena, $this->basedatos);
        if ($this->conexion->connect_error) {
            die("Error de conexión: " . $this->conexion->connect_error);
        }
    }

    public function seleccionar($tabla) {
        $sql = "SELECT * FROM $tabla";
        $resultado = $this->conexion->query($sql);

        $datos = [];
        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        return json_encode($datos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    }

    public function buscar($tabla, $columna, $valor) {
        $sql = "SELECT * FROM $tabla WHERE $columna LIKE ?";
        $stmt = $this->conexion->prepare($sql);
        $like = "%" . $valor . "%";
        $stmt->bind_param("s", $like);
        $stmt->execute();

        $resultado = $stmt->get_result();
        $datos = [];
        while ($fila = $resultado->fetch_assoc()) {
            $datos[] = $fila;
        }

        return json_encode($datos, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    }
}

// Ejemplo de uso
$conexion = new JVDB("localhost", "blog2526", "blog2526", "blog2526");
echo $conexion->buscar("entradas", "titulo", "responsivo");
