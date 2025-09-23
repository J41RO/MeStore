# ~/tests/models/test_system_setting_model_comprehensive_tdd.py
# ---------------------------------------------------------------------------------------------
# MeStore - Comprehensive TDD Tests for SystemSetting Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# TDD SPECIALIST COMPREHENSIVE COVERAGE MISSION
# Model: app/models/system_setting.py
# Target Coverage: 85%+
# Methodology: RED-GREEN-REFACTOR
#
# COVERAGE ANALYSIS:
# - Basic CRUD operations and validation
# - Type conversion and validation
# - Default value handling
# - Category-based organization
# - Access control (public/editable flags)
# - Default settings generation
# - Edge cases and error handling
# ---------------------------------------------------------------------------------------------

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


class TestSystemSettingBasics:
    """TDD: Test basic SystemSetting model functionality"""

    @pytest.mark.tdd
    def test_system_setting_creation_minimal(self, db_session):
        """Test creating system setting with minimal fields"""
        setting = SystemSetting(
            key="test_setting",
            value="test_value",
            category="test",
            data_type="string",
            description="Test setting description"
        )
        db_session.add(setting)
        db_session.commit()

        assert setting.id is not None
        assert setting.key == "test_setting"
        assert setting.value == "test_value"
        assert setting.category == "test"
        assert setting.data_type == "string"
        assert setting.description == "Test setting description"

    @pytest.mark.tdd
    def test_system_setting_creation_all_fields(self, db_session):
        """Test creating system setting with all fields"""
        setting = SystemSetting(
            key="comprehensive_setting",
            value="comprehensive_value",
            category="general",
            data_type="string",
            description="Comprehensive test setting",
            default_value="default_val",
            is_public=True,
            is_editable=False,
            last_modified_by=1
        )
        db_session.add(setting)
        db_session.commit()

        assert setting.key == "comprehensive_setting"
        assert setting.default_value == "default_val"
        assert setting.is_public is True
        assert setting.is_editable is False
        assert setting.last_modified_by == 1

    @pytest.mark.tdd
    def test_system_setting_default_values(self, db_session):
        """Test SystemSetting default values"""
        setting = SystemSetting(
            key="default_test",
            value="test",
            category="test",
            data_type="string",
            description="Test defaults"
        )

        assert setting.is_public is False  # Default should be False
        assert setting.is_editable is True  # Default should be True

    @pytest.mark.tdd
    def test_system_setting_unique_key_constraint(self, db_session):
        """Test unique constraint on key field"""
        setting1 = SystemSetting(
            key="unique_key",
            value="value1",
            category="test",
            data_type="string",
            description="First setting"
        )
        setting2 = SystemSetting(
            key="unique_key",  # Same key
            value="value2",
            category="test",
            data_type="string",
            description="Second setting"
        )

        db_session.add(setting1)
        db_session.commit()

        db_session.add(setting2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestSystemSettingTypeConversion:
    """TDD: Test type conversion functionality"""

    @pytest.mark.tdd
    def test_get_typed_value_string(self, db_session):
        """Test get_typed_value for string type"""
        setting = SystemSetting(
            key="string_setting",
            value="test_string",
            category="test",
            data_type="string",
            description="String test"
        )

        result = setting.get_typed_value()
        assert result == "test_string"
        assert isinstance(result, str)

    @pytest.mark.tdd
    def test_get_typed_value_integer(self, db_session):
        """Test get_typed_value for integer type"""
        setting = SystemSetting(
            key="int_setting",
            value="42",
            category="test",
            data_type="integer",
            description="Integer test"
        )

        result = setting.get_typed_value()
        assert result == 42
        assert isinstance(result, int)

    @pytest.mark.tdd
    def test_get_typed_value_float(self, db_session):
        """Test get_typed_value for float type"""
        setting = SystemSetting(
            key="float_setting",
            value="3.14",
            category="test",
            data_type="float",
            description="Float test"
        )

        result = setting.get_typed_value()
        assert result == 3.14
        assert isinstance(result, float)

    @pytest.mark.tdd
    def test_get_typed_value_boolean_true(self, db_session):
        """Test get_typed_value for boolean type (true values)"""
        true_values = ["true", "1", "yes", "on", "TRUE", "True"]

        for value in true_values:
            setting = SystemSetting(
                key="bool_setting",
                value=value,
                category="test",
                data_type="boolean",
                description="Boolean test"
            )

            result = setting.get_typed_value()
            assert result is True

    @pytest.mark.tdd
    def test_get_typed_value_boolean_false(self, db_session):
        """Test get_typed_value for boolean type (false values)"""
        false_values = ["false", "0", "no", "off", "FALSE", "False", "anything"]

        for value in false_values:
            setting = SystemSetting(
                key="bool_setting",
                value=value,
                category="test",
                data_type="boolean",
                description="Boolean test"
            )

            result = setting.get_typed_value()
            assert result is False

    @pytest.mark.tdd
    def test_get_typed_value_json_valid(self, db_session):
        """Test get_typed_value for valid JSON"""
        json_data = {"key": "value", "number": 42, "array": [1, 2, 3]}
        setting = SystemSetting(
            key="json_setting",
            value=json.dumps(json_data),
            category="test",
            data_type="json",
            description="JSON test"
        )

        result = setting.get_typed_value()
        assert result == json_data
        assert isinstance(result, dict)

    @pytest.mark.tdd
    def test_get_typed_value_json_invalid(self, db_session):
        """Test get_typed_value for invalid JSON falls back to default"""
        setting = SystemSetting(
            key="json_setting",
            value="invalid_json{",
            category="test",
            data_type="json",
            description="JSON test",
            default_value='{"default": true}'
        )

        result = setting.get_typed_value()
        assert result == {"default": True}

    @pytest.mark.tdd
    def test_get_typed_value_empty_returns_default(self, db_session):
        """Test get_typed_value with empty value returns default"""
        setting = SystemSetting(
            key="empty_setting",
            value="",
            category="test",
            data_type="integer",
            description="Empty test",
            default_value="100"
        )

        result = setting.get_typed_value()
        assert result == 100

    @pytest.mark.tdd
    def test_get_typed_value_conversion_error_fallback(self, db_session):
        """Test get_typed_value conversion error falls back to default"""
        setting = SystemSetting(
            key="error_setting",
            value="not_a_number",
            category="test",
            data_type="integer",
            description="Error test",
            default_value="50"
        )

        result = setting.get_typed_value()
        assert result == 50


class TestSystemSettingDefaultValues:
    """TDD: Test default value handling"""

    @pytest.mark.tdd
    def test_get_default_typed_value_string(self, db_session):
        """Test get_default_typed_value for string type"""
        setting = SystemSetting(
            key="test",
            value="current",
            category="test",
            data_type="string",
            description="Test",
            default_value="default_string"
        )

        result = setting.get_default_typed_value()
        assert result == "default_string"

    @pytest.mark.tdd
    def test_get_default_typed_value_integer(self, db_session):
        """Test get_default_typed_value for integer type"""
        setting = SystemSetting(
            key="test",
            value="100",
            category="test",
            data_type="integer",
            description="Test",
            default_value="50"
        )

        result = setting.get_default_typed_value()
        assert result == 50

    @pytest.mark.tdd
    def test_get_default_typed_value_boolean(self, db_session):
        """Test get_default_typed_value for boolean type"""
        setting = SystemSetting(
            key="test",
            value="false",
            category="test",
            data_type="boolean",
            description="Test",
            default_value="true"
        )

        result = setting.get_default_typed_value()
        assert result is True

    @pytest.mark.tdd
    def test_get_default_typed_value_json(self, db_session):
        """Test get_default_typed_value for JSON type"""
        default_json = {"default": True}
        setting = SystemSetting(
            key="test",
            value='{"current": true}',
            category="test",
            data_type="json",
            description="Test",
            default_value=json.dumps(default_json)
        )

        result = setting.get_default_typed_value()
        assert result == default_json

    @pytest.mark.tdd
    def test_get_default_typed_value_no_default(self, db_session):
        """Test get_default_typed_value with no default value"""
        setting = SystemSetting(
            key="test",
            value="current",
            category="test",
            data_type="integer",
            description="Test",
            default_value=None
        )

        result = setting.get_default_typed_value()
        assert result == 0  # System default for integer

    @pytest.mark.tdd
    def test_get_type_default_all_types(self, db_session):
        """Test _get_type_default for all supported types"""
        setting = SystemSetting(
            key="test",
            value="test",
            category="test",
            data_type="string",
            description="Test"
        )

        # Test all type defaults
        setting.data_type = "string"
        assert setting._get_type_default() == ""

        setting.data_type = "integer"
        assert setting._get_type_default() == 0

        setting.data_type = "float"
        assert setting._get_type_default() == 0.0

        setting.data_type = "boolean"
        assert setting._get_type_default() is False

        setting.data_type = "json"
        assert setting._get_type_default() == {}

        setting.data_type = "unknown"
        assert setting._get_type_default() == ""


class TestSystemSettingValueSetting:
    """TDD: Test set_typed_value functionality"""

    @pytest.mark.tdd
    def test_set_typed_value_boolean_true(self, db_session):
        """Test set_typed_value for boolean True"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="boolean",
            description="Test"
        )

        setting.set_typed_value(True)
        assert setting.value == "true"

    @pytest.mark.tdd
    def test_set_typed_value_boolean_false(self, db_session):
        """Test set_typed_value for boolean False"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="boolean",
            description="Test"
        )

        setting.set_typed_value(False)
        assert setting.value == "false"

    @pytest.mark.tdd
    def test_set_typed_value_boolean_string_conversion(self, db_session):
        """Test set_typed_value for boolean with string input"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="boolean",
            description="Test"
        )

        setting.set_typed_value("yes")
        assert setting.value == "true"

        setting.set_typed_value("no")
        assert setting.value == "false"

    @pytest.mark.tdd
    def test_set_typed_value_integer(self, db_session):
        """Test set_typed_value for integer"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="integer",
            description="Test"
        )

        setting.set_typed_value(42)
        assert setting.value == "42"

        setting.set_typed_value("100")
        assert setting.value == "100"

    @pytest.mark.tdd
    def test_set_typed_value_float(self, db_session):
        """Test set_typed_value for float"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="float",
            description="Test"
        )

        setting.set_typed_value(3.14)
        assert setting.value == "3.14"

        setting.set_typed_value("2.71")
        assert setting.value == "2.71"

    @pytest.mark.tdd
    def test_set_typed_value_json_dict(self, db_session):
        """Test set_typed_value for JSON with dict"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="json",
            description="Test"
        )

        test_dict = {"key": "value", "number": 42}
        setting.set_typed_value(test_dict)

        assert setting.value == json.dumps(test_dict)

    @pytest.mark.tdd
    def test_set_typed_value_json_list(self, db_session):
        """Test set_typed_value for JSON with list"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="json",
            description="Test"
        )

        test_list = [1, 2, 3, "four"]
        setting.set_typed_value(test_list)

        assert setting.value == json.dumps(test_list)

    @pytest.mark.tdd
    def test_set_typed_value_json_string(self, db_session):
        """Test set_typed_value for JSON with string input"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="json",
            description="Test"
        )

        setting.set_typed_value("string_value")
        assert setting.value == "string_value"

    @pytest.mark.tdd
    def test_set_typed_value_string(self, db_session):
        """Test set_typed_value for string"""
        setting = SystemSetting(
            key="test",
            value="",
            category="test",
            data_type="string",
            description="Test"
        )

        setting.set_typed_value("test_string")
        assert setting.value == "test_string"

        setting.set_typed_value(123)
        assert setting.value == "123"


class TestSystemSettingDefaultSettings:
    """TDD: Test default settings generation"""

    @pytest.mark.tdd
    def test_get_default_settings_returns_list(self, db_session):
        """Test get_default_settings returns proper list"""
        defaults = SystemSetting.get_default_settings()

        assert isinstance(defaults, list)
        assert len(defaults) > 0

    @pytest.mark.tdd
    def test_get_default_settings_contains_required_fields(self, db_session):
        """Test get_default_settings contains all required fields"""
        defaults = SystemSetting.get_default_settings()

        required_fields = ['key', 'value', 'category', 'data_type', 'description', 'default_value', 'is_public', 'is_editable']

        for setting in defaults:
            for field in required_fields:
                assert field in setting, f"Missing field {field} in setting {setting.get('key')}"

    @pytest.mark.tdd
    def test_get_default_settings_categories(self, db_session):
        """Test get_default_settings includes expected categories"""
        defaults = SystemSetting.get_default_settings()
        categories = set(setting['category'] for setting in defaults)

        expected_categories = {'general', 'email', 'business', 'security'}
        assert expected_categories.issubset(categories)

    @pytest.mark.tdd
    def test_get_default_settings_data_types(self, db_session):
        """Test get_default_settings includes various data types"""
        defaults = SystemSetting.get_default_settings()
        data_types = set(setting['data_type'] for setting in defaults)

        expected_types = {'string', 'integer', 'boolean', 'float'}
        assert expected_types.issubset(data_types)

    @pytest.mark.tdd
    def test_get_default_settings_specific_settings(self, db_session):
        """Test get_default_settings includes specific expected settings"""
        defaults = SystemSetting.get_default_settings()
        settings_by_key = {setting['key']: setting for setting in defaults}

        # Test specific settings exist
        assert 'site_name' in settings_by_key
        assert 'maintenance_mode' in settings_by_key
        assert 'default_commission_rate' in settings_by_key
        assert 'max_login_attempts' in settings_by_key
        assert 'email_notifications_enabled' in settings_by_key

        # Test specific setting properties
        site_name = settings_by_key['site_name']
        assert site_name['category'] == 'general'
        assert site_name['data_type'] == 'string'
        assert site_name['is_public'] is True

        maintenance_mode = settings_by_key['maintenance_mode']
        assert maintenance_mode['data_type'] == 'boolean'
        assert maintenance_mode['is_public'] is False

    @pytest.mark.tdd
    def test_get_default_settings_commission_rates(self, db_session):
        """Test commission rate settings have correct values"""
        defaults = SystemSetting.get_default_settings()
        settings_by_key = {setting['key']: setting for setting in defaults}

        default_rate = settings_by_key['default_commission_rate']
        min_rate = settings_by_key['min_commission_rate']
        max_rate = settings_by_key['max_commission_rate']

        assert default_rate['value'] == '0.15'
        assert min_rate['value'] == '0.05'
        assert max_rate['value'] == '0.30'
        assert all(setting['data_type'] == 'float' for setting in [default_rate, min_rate, max_rate])

    @pytest.mark.tdd
    def test_get_default_settings_security_settings(self, db_session):
        """Test security settings have appropriate values"""
        defaults = SystemSetting.get_default_settings()
        settings_by_key = {setting['key']: setting for setting in defaults}

        session_timeout = settings_by_key['session_timeout_minutes']
        max_attempts = settings_by_key['max_login_attempts']
        password_length = settings_by_key['password_min_length']

        assert session_timeout['value'] == '120'
        assert max_attempts['value'] == '5'
        assert password_length['value'] == '8'
        assert all(setting['category'] == 'security' for setting in [session_timeout, max_attempts, password_length])


class TestSystemSettingRepresentation:
    """TDD: Test string representation methods"""

    @pytest.mark.tdd
    def test_repr_method(self, db_session):
        """Test __repr__ method"""
        setting = SystemSetting(
            key="test_setting",
            value="a very long value that should be truncated in the representation",
            category="test",
            data_type="string",
            description="Test setting"
        )

        repr_str = repr(setting)

        assert "SystemSetting" in repr_str
        assert "test_setting" in repr_str
        assert "test" in repr_str
        assert "..." in repr_str  # Should be truncated

    @pytest.mark.tdd
    def test_repr_method_short_value(self, db_session):
        """Test __repr__ method with short value"""
        setting = SystemSetting(
            key="short_setting",
            value="short",
            category="test",
            data_type="string",
            description="Test setting"
        )

        repr_str = repr(setting)

        assert "SystemSetting" in repr_str
        assert "short_setting" in repr_str
        assert "short" in repr_str


class TestSystemSettingEdgeCases:
    """TDD: Test edge cases and error conditions"""

    @pytest.mark.tdd
    def test_conversion_error_fallback_behavior(self, db_session):
        """Test behavior when type conversion fails"""
        setting = SystemSetting(
            key="error_test",
            value="not_a_number",
            category="test",
            data_type="integer",
            description="Error test"
        )

        # Should fallback to system default (0) when no default_value
        result = setting.get_typed_value()
        assert result == 0

    @pytest.mark.tdd
    def test_default_value_conversion_error(self, db_session):
        """Test behavior when default value conversion fails"""
        setting = SystemSetting(
            key="default_error_test",
            value="current_value",
            category="test",
            data_type="integer",
            description="Error test",
            default_value="not_a_number"
        )

        # Should fallback to system default when default_value conversion fails
        result = setting.get_default_typed_value()
        assert result == 0

    @pytest.mark.tdd
    def test_empty_category_and_description(self, db_session):
        """Test with empty category and description"""
        setting = SystemSetting(
            key="empty_test",
            value="test",
            category="",
            data_type="string",
            description=""
        )

        # Should still work
        assert setting.get_typed_value() == "test"

    @pytest.mark.tdd
    def test_none_last_modified_by(self, db_session):
        """Test with None last_modified_by"""
        setting = SystemSetting(
            key="none_modifier",
            value="test",
            category="test",
            data_type="string",
            description="Test",
            last_modified_by=None
        )

        db_session.add(setting)
        db_session.commit()

        assert setting.last_modified_by is None

    @pytest.mark.tdd
    def test_created_at_and_updated_at_timestamps(self, db_session):
        """Test automatic timestamp generation"""
        setting = SystemSetting(
            key="timestamp_test",
            value="test",
            category="test",
            data_type="string",
            description="Test"
        )

        db_session.add(setting)
        db_session.commit()

        assert setting.created_at is not None
        assert setting.updated_at is not None
        assert isinstance(setting.created_at, datetime)
        assert isinstance(setting.updated_at, datetime)

    @pytest.mark.tdd
    def test_case_sensitivity_boolean_conversion(self, db_session):
        """Test case sensitivity in boolean conversion"""
        setting = SystemSetting(
            key="case_test",
            value="",
            category="test",
            data_type="boolean",
            description="Test"
        )

        # Test various case combinations
        test_cases = [
            ("TRUE", True),
            ("True", True),
            ("tRuE", True),
            ("FALSE", False),
            ("False", False),
            ("fAlSe", False),
            ("YES", True),
            ("NO", False),
            ("ON", True),
            ("OFF", False)
        ]

        for value, expected in test_cases:
            setting.value = value
            assert setting.get_typed_value() == expected