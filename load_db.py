import resys.database
deb = 'db/resys.db'
db = resys.database.ResysDatabase(deb)
#db.clean()
db.load_init_values()

