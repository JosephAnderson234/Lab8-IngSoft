from rewards.config import BROKER_KAFKA, BROKER_MEMORIA, Configuracion


def test_valores_por_defecto():
    config = Configuracion()
    assert config.tipo_broker == BROKER_MEMORIA
    assert config.password == ""  # nunca hay secretos por defecto


def test_desde_entorno_lee_variables():
    entorno = {
        "BROKER_TIPO": BROKER_KAFKA,
        "BROKER_HOST": "192.0.2.10",
        "BROKER_PUERTO": "9092",
        "BROKER_USUARIO": "test_user",
        "BROKER_PASSWORD": "secreto",
        "COLA_TRANSACCIONES": "tx",
        "GRUPO_CONSUMIDOR": "g1",
    }
    config = Configuracion.desde_entorno(entorno)
    assert config.tipo_broker == BROKER_KAFKA
    assert config.host == "192.0.2.10"
    assert config.puerto == 9092
    assert config.usuario == "test_user"
    assert config.password == "secreto"
    assert config.cola_transacciones == "tx"
    assert config.grupo_consumidor == "g1"


def test_desde_entorno_usa_defaults_si_falta():
    config = Configuracion.desde_entorno({})
    assert config.host == "localhost"
    assert config.puerto == 5672
