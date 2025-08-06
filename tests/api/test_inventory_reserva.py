def test_reservar_stock_endpoint_exists():
    from app.api.v1.endpoints.inventory import reservar_stock
    assert callable(reservar_stock)
    print("✅ Endpoint reservar_stock existe")

def test_reserva_schemas_exist():
    from app.schemas.inventory import ReservaStockCreate, ReservaResponse
    print("✅ Schemas de reserva disponibles")

if __name__ == "__main__":
    test_reservar_stock_endpoint_exists()  
    test_reserva_schemas_exist()
