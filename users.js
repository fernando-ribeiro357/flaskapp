db = connect('mongodb://localhost/pessoa');

db.users.insertMany([
    {
        "name":"Administrador",
        "password":"$pbkdf2-sha256$29000$YgzBWEtpzTmnFKJ0LgWA0A$sJG1FBiaF8rPz6V9UU6usFMI8qD0wnOijMDL2sJnt0o", /* senha123 */
        "profile":"sysadmin",
        "username":"admin",
        "email":"admin@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    },
    {
        "name":"Fernando Ribeiro",
        "password":"$pbkdf2-sha256$29000$YgzBWEtpzTmnFKJ0LgWA0A$sJG1FBiaF8rPz6V9UU6usFMI8qD0wnOijMDL2sJnt0o", /* senha123 */
        "profile":"user",
        "username":"fernando",
        "email":"fernando@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    },
    {
        "name":"Tarsila Mancebo",
        "password":"$pbkdf2-sha256$29000$YgzBWEtpzTmnFKJ0LgWA0A$sJG1FBiaF8rPz6V9UU6usFMI8qD0wnOijMDL2sJnt0o", /* senha123 */
        "profile":"user",
        "username":"tarsila",
        "email":"tarsila@flaskapp.local",
        "created_at": new Date(),
        "updated_at": null,
        "deleted_at": null
    }
]);