from rewards.domain import seguridad


def test_normalizar_tarjeta_elimina_separadores():
    assert seguridad.normalizar_tarjeta("4111-1111 1111_1111") == "4111111111111111"


def test_normalizar_tarjeta_none():
    assert seguridad.normalizar_tarjeta(None) == ""


def test_enmascarar_muestra_ultimos_cuatro():
    assert seguridad.enmascarar_tarjeta("4111111111111234").endswith("1234")
    assert "1234" in seguridad.enmascarar_tarjeta("4111111111111234")


def test_enmascarar_tarjeta_corta():
    assert seguridad.enmascarar_tarjeta("12") == "****"


def test_identificador_cuenta_estable_y_no_reversible():
    id1 = seguridad.identificador_cuenta("4111 1111 1111 1111")
    id2 = seguridad.identificador_cuenta("4111111111111111")
    assert id1 == id2  # mismo numero, mismo id
    assert "4111" not in id1  # no expone el numero real
    assert len(id1) == 64  # sha-256 en hex
