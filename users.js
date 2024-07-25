db = connect('mongodb://localhost/pessoa');

db.users.insertMany([
    {
        "name":"Fernando Ribeiro",
        "password":"senha123",
        "profile":"sysadmin",
        "username":"fernando",
        "email":"fernando@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    },
    {
        "name":"Oswaldo Gomes",
        "password":"senha123",
        "profile":"user",
        "username":"oswaldo",
        "email":"oswaldo@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    },
    {
        "name":"Arminda Almeirinda",
        "password":"senha123",
        "profile":"user",
        "username":"arminda",
        "email":"arminda@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    }
]);