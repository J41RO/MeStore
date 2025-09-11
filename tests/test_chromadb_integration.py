#!/usr/bin/env python3
"""
Script de prueba realista para ChromaDB y embeddings.
Valida todo el pipeline con productos del marketplace colombiano.
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.embeddings import add_items, query_similar, get_collection_stats

def test_marketplace_products():
    """Probar con productos realistas del marketplace."""
    print("=== 🛒 PRUEBA MARKETPLACE COLOMBIANO ===")
    
    # Productos realistas colombianos
    productos = [
        "Café Juan Valdez Origen Huila 500g premium",
        "Arepa de maíz blanco precocida Harina PAN 1kg",
        "Aguacate Hass fresco de Antioquia por unidad",
        "Panela orgánica de caña Los Llanos 500g",
        "Bocadillo veleño de guayaba Montes 150g",
        "Chocolate Corona tableta tradicional 250g",
        "Arroz Diana premium grano largo 2.5kg",
        "Fríjol cargamanto rojo de Antioquia 500g"
    ]
    
    ids = [f"prod_{i:03d}" for i in range(1, len(productos) + 1)]
    
    metadatos = [
        {"categoria": "bebidas", "origen": "huila", "precio": 15000, "organico": True},
        {"categoria": "harinas", "origen": "nacional", "precio": 3500, "organico": False},
        {"categoria": "frutas", "origen": "antioquia", "precio": 2500, "organico": True},
        {"categoria": "endulzantes", "origen": "llanos", "precio": 4500, "organico": True},
        {"categoria": "dulces", "origen": "santander", "precio": 3000, "organico": False},
        {"categoria": "chocolates", "origen": "nacional", "precio": 4000, "organico": False},
        {"categoria": "cereales", "origen": "nacional", "precio": 8500, "organico": False},
        {"categoria": "legumbres", "origen": "antioquia", "precio": 6500, "organico": True}
    ]
    
    # Agregar productos
    print("📦 Agregando productos al vector store...")
    success = add_items("products", ids, productos, metadatos)
    
    if success:
        print(f"✅ {len(productos)} productos agregados exitosamente")
        
        # Estadísticas
        stats = get_collection_stats("products")
        print(f"📊 Total items en colección: {stats['count']}")
        
        assert True
    else:
        print("❌ Error agregando productos")
        assert False, "Failed to add products to ChromaDB"

def test_semantic_queries():
    """Probar consultas semánticas realistas."""
    print("\n=== 🔍 PRUEBAS DE BÚSQUEDA SEMÁNTICA ===")
    
    consultas_prueba = [
        ("bebida caliente colombiana", "debería encontrar café"),
        ("masa para hacer arepas", "debería encontrar harina de maíz"),
        ("fruta verde cremosa", "debería encontrar aguacate"),
        ("endulzante natural orgánico", "debería encontrar panela"),
        ("postre típico santandereano", "debería encontrar bocadillo"),
        ("producto orgánico de Antioquia", "debería encontrar fríjol o aguacate")
    ]
    
    resultados_exitosos = 0
    
    for consulta, expectativa in consultas_prueba:
        print(f"\n🔍 Consultando: '{consulta}'")
        print(f"   Expectativa: {expectativa}")
        
        try:
            resultados = query_similar("products", consulta, n_results=3)
            
            if resultados and resultados['ids']:
                ids = resultados['ids'] if isinstance(resultados['ids'], list) else [resultados['ids']]
                docs = resultados['documents'] if isinstance(resultados['documents'], list) else [resultados['documents']]
                distances = resultados['distances'] if isinstance(resultados['distances'], list) else [resultados['distances']]
                
                print(f"   📋 Encontrados {len(ids)} resultados:")
                
                for i, (doc_id, documento, distancia) in enumerate(zip(
                    ids[:2],  # Solo primeros 2
                    docs[:2],
                    distances[:2]
                )):
                    similitud = 1.0 - distancia
                    print(f"   {i+1}. {documento[:60]}... (similitud: {similitud:.3f})")
                
                resultados_exitosos += 1
            else:
                print("   ❌ No se encontraron resultados")
                
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
    
    print(f"\n📊 Consultas exitosas: {resultados_exitosos}/{len(consultas_prueba)}")
    assert resultados_exitosos == len(consultas_prueba), f"Only {resultados_exitosos}/{len(consultas_prueba)} queries were successful"

def test_filtered_search():
    """Probar búsquedas con filtros."""
    print("\n=== 🎯 PRUEBAS CON FILTROS ===")
    
    try:
        # Buscar solo productos orgánicos
        print("🔍 Buscando productos orgánicos...")
        resultados_organicos = query_similar(
            "products", 
            "producto natural saludable", 
            n_results=10,
            where={"organico": True}
        )
        
        print(f"   📋 Productos orgánicos encontrados: {len(resultados_organicos['ids'][0])}")
        
        # Buscar por región específica
        print("\n🔍 Buscando productos de Antioquia...")
        resultados_antioquia = query_similar(
            "products",
            "producto regional",
            n_results=10, 
            where={"origen": "antioquia"}
        )
        
        print(f"   📋 Productos de Antioquia: {len(resultados_antioquia['ids'][0])}")
        
        # Buscar por rango de precio
        print("\n💰 Buscando productos económicos (<5000)...")
        resultados_economicos = query_similar(
            "products",
            "producto barato",
            n_results=10,
            where={"precio": {"$lt": 5000}}
        )
        
        print(f"   📋 Productos económicos: {len(resultados_economicos['ids'][0])}")
        
        assert True
        
    except Exception as e:
        print(f"❌ Error en búsquedas filtradas: {e}")
        assert False, f"Filtered search failed: {e}"

def main():
    """Ejecutar todas las pruebas."""
    print("🚀 INICIANDO PRUEBAS CHROMADB - MARKETPLACE COLOMBIANO")
    print("=" * 60)
    
    pruebas = [
        test_marketplace_products,
        test_semantic_queries,
        test_filtered_search
    ]
    
    exitosas = 0
    
    for prueba in pruebas:
        try:
            if prueba():
                exitosas += 1
                print(f"✅ {prueba.__name__} EXITOSA")
            else:
                print(f"❌ {prueba.__name__} FALLÓ")
        except Exception as e:
            print(f"❌ {prueba.__name__} ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: {exitosas}/{len(pruebas)} pruebas exitosas")
    
    if exitosas == len(pruebas):
        print("🎉 ✅ TODAS LAS PRUEBAS CHROMADB EXITOSAS")
        print("🚀 SISTEMA DE VECTOR SEARCH COMPLETAMENTE FUNCIONAL")
        return True
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
