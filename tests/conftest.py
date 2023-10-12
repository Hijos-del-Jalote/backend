import os
import pytest
from .populate_db import populate_db
from db.models import *

# Fixture para configurar la base de datos antes de ciertas pruebas
@pytest.fixture(scope="function")
def setup_db_before_test(request):
    os.environ["ENVIRONMENT"] = "TEST"
    populate_db()
    

# Fixture para realizar la limpieza después de la prueba
@pytest.fixture(scope="function")
def cleanup_db_after_test(request):
    file_to_cleanup = "db/database_test.sqlite"
    yield
    with db_session:
        db.execute('delete from "%s"' % Jugador._table_)
        db.execute("delete from sqlite_sequence where name='%s'" \
                                   % Jugador._table_)

        db.execute('delete from "%s"' % Partida._table_)
        db.execute("delete from sqlite_sequence where name='%s'" \
                                   % Partida._table_)

        db.execute('delete from "%s"' % Carta._table_)
        db.execute("delete from sqlite_sequence where name='%s'" \
                                   % Carta._table_)
    
        db.execute('delete from "%s"' % TemplateCarta._table_)
        db.execute("delete from sqlite_sequence where name='%s'" \
                                   % TemplateCarta._table_)
    
    

    

