db.clientes.updateMany(
    {nombre:'Jorge'},
    {
        $set:
        {telefono:"1111111"}
    }
)