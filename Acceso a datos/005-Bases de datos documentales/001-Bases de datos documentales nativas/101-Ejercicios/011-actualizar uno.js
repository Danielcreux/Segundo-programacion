db.clientes.updateOne(
    {nombre:'Joshue Daniel'},
    {
        $set:
        {email:"info@johue.com"}
    }
)