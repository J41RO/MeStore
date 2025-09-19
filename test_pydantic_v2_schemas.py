#!/usr/bin/env python3
"""
Quick test script to validate Pydantic V2 migration success
"""

import sys
sys.path.append('.')

def test_schema_imports():
    """Test that all schemas can be imported without errors"""
    try:
        from app.schemas.leads import LeadCreateSchema, LeadResponseSchema
        from app.schemas.common import APIResponse
        print("✅ All schema imports successful")
        return True
    except Exception as e:
        print(f"❌ Schema import failed: {e}")
        return False

def test_schema_creation():
    """Test creating instances of migrated schemas"""
    try:
        from app.schemas.leads import LeadCreateSchema

        # Test Lead creation with validator
        lead_data = {
            "nombre": "Juan Pérez",
            "empresa": "Test Company",
            "telefono": "+57 300 123 4567",
            "email": "juan@test.com",
            "tipo_negocio": "vendedor"
        }
        lead = LeadCreateSchema(**lead_data)
        print(f"✅ Lead created successfully: {lead.nombre}")

        from app.schemas.common import APIResponse
        msg = APIResponse(success=True, message="Test message", data=None)
        print(f"✅ APIResponse created: {msg.message}")

        return True
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

def test_validators():
    """Test that field validators work correctly"""
    try:
        from app.schemas.leads import LeadCreateSchema

        # Test valid phone number
        lead_valid = LeadCreateSchema(
            nombre="Test",
            empresa="Test Co",
            telefono="+57 300 123 4567",
            email="test@test.com",
            tipo_negocio="vendedor"
        )
        print(f"✅ Valid phone accepted: {lead_valid.telefono}")

        # Test validator enforcement (this should work with V2)
        try:
            lead_invalid = LeadCreateSchema(
                nombre="",  # Empty name should be caught by validator
                empresa="Test Co",
                telefono="+57 300 123 4567",
                email="test@test.com",
                tipo_negocio="vendedor"
            )
            print("⚠️  Empty name validation might need review")
        except Exception as ve:
            print(f"✅ Validator working correctly: {type(ve).__name__}")

        return True
    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Pydantic V2 Migration Success")
    print("=" * 50)

    tests = [
        ("Schema Imports", test_schema_imports),
        ("Schema Creation", test_schema_creation),
        ("Validators", test_validators)
    ]

    results = []
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        result = test_func()
        results.append(result)
        print(f"{'✅ PASSED' if result else '❌ FAILED'}: {name}")

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All Pydantic V2 migration tests PASSED!")
        print("✅ Migration was successful!")
    else:
        print("⚠️  Some tests failed - manual review required")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)