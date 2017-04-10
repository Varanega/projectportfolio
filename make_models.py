# Crea el esquema de la base de datos
from models import db
# Delete Delete all
db.reflect()
db.drop_all()
db.create_all()