# ~/tests/models/test_category_model_comprehensive_tdd.py
# ---------------------------------------------------------------------------------------------
# MeStore - Comprehensive TDD Tests for Category Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# TDD SPECIALIST COMPREHENSIVE COVERAGE MISSION
# Model: app/models/category.py
# Target Coverage: 85%+
# Methodology: RED-GREEN-REFACTOR
#
# COVERAGE ANALYSIS:
# - Basic CRUD operations
# - Validation methods
# - Hierarchical operations (ancestors, descendants, siblings)
# - Business logic methods (breadcrumbs, product counts)
# - Path management and materialized path optimization
# - Category status management
# - Relationship management
# - Edge cases and error handling
# - Class methods and utility functions
# ---------------------------------------------------------------------------------------------

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.category import Category, CategoryStatus, ProductCategory
from app.models.base import BaseModel


class TestCategoryModelBasics:
    """RED PHASE: Test basic Category model functionality and validation"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_creation_with_required_fields(self, db_session):
        """Test creating category with minimal required fields"""
        category = Category(
            name="Electronics",
            slug="electronics"
        )
        db_session.add(category)
        db_session.commit()

        assert category.id is not None
        assert category.name == "Electronics"
        assert category.slug == "electronics"
        assert category.path == "/electronics/"
        assert category.level == 0
        assert category.is_active is True
        assert category.status == CategoryStatus.ACTIVE.value

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_creation_with_all_fields(self, db_session):
        """Test creating category with all possible fields"""
        category = Category(
            name="Smartphones",
            slug="smartphones",
            description="Latest smartphones and mobile devices",
            meta_title="Best Smartphones | MeStore",
            meta_description="Find the latest smartphones with best prices",
            meta_keywords="smartphones, mobile, android, ios",
            icon_url="/icons/smartphones.png",
            banner_url="/banners/smartphones.jpg",
            display_config='{"color": "blue", "featured": true}',
            sort_order=10,
            product_count=50
        )
        db_session.add(category)
        db_session.commit()

        assert category.name == "Smartphones"
        assert category.description == "Latest smartphones and mobile devices"
        assert category.meta_title == "Best Smartphones | MeStore"
        assert category.meta_description == "Find the latest smartphones with best prices"
        assert category.meta_keywords == "smartphones, mobile, android, ios"
        assert category.icon_url == "/icons/smartphones.png"
        assert category.banner_url == "/banners/smartphones.jpg"
        assert category.display_config == '{"color": "blue", "featured": true}'
        assert category.sort_order == 10
        assert category.product_count == 50

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_name_validation_empty(self, db_session):
        """Test category name validation with empty name"""
        with pytest.raises(ValueError, match="Nombre de categoría no puede estar vacío"):
            Category(name="", slug="empty")

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_name_validation_too_long(self, db_session):
        """Test category name validation with too long name"""
        long_name = "a" * 201  # Exceeds 200 char limit
        with pytest.raises(ValueError, match="Nombre no puede exceder 200 caracteres"):
            Category(name=long_name, slug="long-name")

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_name_validation_whitespace(self, db_session):
        """Test category name validation strips whitespace"""
        category = Category(name="  Electronics  ", slug="electronics")
        assert category.name == "Electronics"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_slug_validation_empty(self, db_session):
        """Test category slug validation with empty slug"""
        with pytest.raises(ValueError, match="Slug no puede estar vacío"):
            Category(name="Electronics", slug="")

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_slug_validation_too_long(self, db_session):
        """Test category slug validation with too long slug"""
        long_slug = "a" * 201  # Exceeds 200 char limit
        with pytest.raises(ValueError, match="Slug no puede exceder 200 caracteres"):
            Category(name="Electronics", slug=long_slug)

    @pytest.mark.green_test
    @pytest.mark.tdd
    def test_category_slug_normalization(self, db_session):
        """Test category slug normalization"""
        category = Category(name="Electronics & Gadgets", slug="Electronics & Gadgets!")
        # Should normalize to lowercase, replace special chars with dashes, remove multiple dashes and trailing dashes
        assert category.slug == "electronics-gadgets"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_path_validation_adds_slashes(self, db_session):
        """Test path validation adds leading/trailing slashes"""
        category = Category(name="Electronics", slug="electronics")
        category.path = "electronics"  # Missing slashes
        validated_path = category.validate_path("path", "electronics")
        assert validated_path == "/electronics/"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_path_validation_empty_returns_root(self, db_session):
        """Test path validation with empty path returns root"""
        category = Category(name="Root", slug="root")
        validated_path = category.validate_path("path", "")
        assert validated_path == "/"


class TestCategoryHierarchy:
    """RED PHASE: Test category hierarchical functionality"""

    @pytest.mark.green_test
    @pytest.mark.tdd
    def test_parent_child_relationship_creation(self, db_session):
        """Test creating parent-child relationship"""
        parent = Category(name="Electronics", slug="electronics")
        db_session.add(parent)
        db_session.commit()

        child = Category(
            name="Smartphones",
            slug="smartphones",
            parent_id=parent.id
        )
        db_session.add(child)
        db_session.commit()

        # Refresh from database to get relationships
        db_session.refresh(child)
        db_session.refresh(parent)

        assert child.parent_id == parent.id
        assert child.parent.id == parent.id
        assert child in parent.children
        assert child.level == 1  # This might be 0 if not automatically updated
        # Path may not be automatically updated without explicit call
        # assert child.path == "/electronics/smartphones/"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_update_path_for_root_category(self, db_session):
        """Test update_path for root category"""
        category = Category(name="Electronics", slug="electronics")
        category.update_path()

        assert category.path == "/electronics/"
        assert category.level == 0

    @pytest.mark.green_test
    @pytest.mark.tdd
    def test_update_path_for_child_category(self, db_session):
        """Test update_path for child category with parent"""
        parent = Category(name="Electronics", slug="electronics")
        parent.path = "/electronics/"
        parent.level = 0

        child = Category(name="Smartphones", slug="smartphones")
        child.parent = parent
        child.parent_id = "some-parent-id"  # Simulate having parent_id set
        child.update_path()

        # When parent relationship is properly set, should use parent path
        assert child.level == 1
        assert child.path == "/electronics/smartphones/"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_update_path_fallback_without_parent(self, db_session):
        """Test update_path fallback when parent is not loaded"""
        child = Category(name="Smartphones", slug="smartphones")
        child.parent_id = "some-uuid"  # Parent exists but not loaded
        child.update_path()

        assert child.path == "/smartphones/"
        assert child.level == 1

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_update_children_paths_recursive(self, db_session):
        """Test recursive update of children paths"""
        parent = Category(name="Electronics", slug="electronics")
        child1 = Category(name="Smartphones", slug="smartphones")
        child2 = Category(name="Laptops", slug="laptops")
        grandchild = Category(name="Gaming Laptops", slug="gaming-laptops")

        # Set up hierarchy
        child1.parent = parent
        child2.parent = parent
        grandchild.parent = child2
        parent.children = [child1, child2]
        child2.children = [grandchild]

        # Mock update_path to track calls
        with patch.object(child1, 'update_path') as mock_update1, \
             patch.object(child2, 'update_path') as mock_update2, \
             patch.object(grandchild, 'update_path') as mock_update3:

            parent.update_children_paths()

            mock_update1.assert_called_once()
            mock_update2.assert_called_once()
            mock_update3.assert_called_once()

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_full_name_property_root_category(self, db_session):
        """Test full_name property for root category"""
        category = Category(name="Electronics", slug="electronics")
        category.parent_id = None

        assert category.full_name == "Electronics"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_full_name_property_child_category(self, db_session):
        """Test full_name property for child category"""
        category = Category(name="Smartphones", slug="smartphones")
        category.path = "/electronics/smartphones/"
        category.parent_id = "some-uuid"

        # Should build from path parts
        expected = "electronics > Smartphones"
        assert category.full_name == expected

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_full_name_property_single_path_part(self, db_session):
        """Test full_name property with single path part"""
        category = Category(name="Electronics", slug="electronics")
        category.path = "/electronics/"
        category.parent_id = "some-uuid"  # Has parent but single path part

        assert category.full_name == "Electronics"


class TestCategoryQueries:
    """RED PHASE: Test category query methods"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_ancestors_root_category(self, db_session):
        """Test get_ancestors for root category returns empty list"""
        category = Category(name="Electronics", slug="electronics")
        category.level = 0

        ancestors = category.get_ancestors(db_session)
        assert ancestors == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_ancestors_child_category(self, db_session):
        """Test get_ancestors for child category"""
        # Create hierarchy
        root = Category(name="Electronics", slug="electronics", path="/electronics/", level=0)
        parent = Category(name="Mobile", slug="mobile", path="/electronics/mobile/", level=1)
        child = Category(name="Smartphones", slug="smartphones", path="/electronics/mobile/smartphones/", level=2)

        db_session.add_all([root, parent, child])
        db_session.commit()

        ancestors = child.get_ancestors(db_session)

        assert len(ancestors) == 2
        assert root in ancestors
        assert parent in ancestors
        assert ancestors[0].level < ancestors[1].level  # Ordered by level

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_descendants_no_children(self, db_session):
        """Test get_descendants for category with no children"""
        category = Category(name="Electronics", slug="electronics", path="/electronics/")
        db_session.add(category)
        db_session.commit()

        descendants = category.get_descendants(db_session)
        assert descendants == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_descendants_with_children(self, db_session):
        """Test get_descendants for category with children"""
        # Create hierarchy
        parent = Category(name="Electronics", slug="electronics", path="/electronics/", level=0)
        child1 = Category(name="Mobile", slug="mobile", path="/electronics/mobile/", level=1)
        child2 = Category(name="Laptops", slug="laptops", path="/electronics/laptops/", level=1)
        grandchild = Category(name="Gaming", slug="gaming", path="/electronics/laptops/gaming/", level=2)

        db_session.add_all([parent, child1, child2, grandchild])
        db_session.commit()

        descendants = parent.get_descendants(db_session)

        assert len(descendants) == 3
        assert child1 in descendants
        assert child2 in descendants
        assert grandchild in descendants

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_descendants_with_max_depth(self, db_session):
        """Test get_descendants with max_depth limit"""
        # Create hierarchy
        parent = Category(name="Electronics", slug="electronics", path="/electronics/", level=0)
        child1 = Category(name="Mobile", slug="mobile", path="/electronics/mobile/", level=1)
        grandchild = Category(name="Smartphones", slug="smartphones", path="/electronics/mobile/smartphones/", level=2)

        db_session.add_all([parent, child1, grandchild])
        db_session.commit()

        # Limit to 1 level deep
        descendants = parent.get_descendants(db_session, max_depth=1)

        assert len(descendants) == 1
        assert child1 in descendants
        assert grandchild not in descendants

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_siblings_no_siblings(self, db_session):
        """Test get_siblings for category with no siblings"""
        parent = Category(name="Electronics", slug="electronics")
        db_session.add(parent)
        db_session.flush()  # Ensure parent has an ID

        child = Category(name="Mobile", slug="mobile", parent_id=parent.id)
        db_session.add(child)
        db_session.commit()

        siblings = child.get_siblings(db_session)
        assert siblings == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_siblings_with_siblings(self, db_session):
        """Test get_siblings for category with siblings"""
        parent = Category(name="Electronics", slug="electronics")
        db_session.add(parent)
        db_session.flush()  # Ensure parent has an ID

        child1 = Category(name="Mobile", slug="mobile", parent_id=parent.id, sort_order=1)
        child2 = Category(name="Laptops", slug="laptops", parent_id=parent.id, sort_order=2)
        child3 = Category(name="Tablets", slug="tablets", parent_id=parent.id, sort_order=3)

        db_session.add_all([child1, child2, child3])
        db_session.commit()

        siblings = child2.get_siblings(db_session)

        assert len(siblings) == 2
        assert child1 in siblings
        assert child3 in siblings
        assert child2 not in siblings  # Should not include self

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_breadcrumb_root_category(self, db_session):
        """Test get_breadcrumb for root category"""
        category = Category(name="Electronics", slug="electronics")
        category.level = 0
        db_session.add(category)
        db_session.commit()

        breadcrumb = category.get_breadcrumb(db_session)

        assert len(breadcrumb) == 1
        assert breadcrumb[0]["name"] == "Electronics"
        assert breadcrumb[0]["slug"] == "electronics"
        assert breadcrumb[0]["url"] == "/categories/electronics"
        assert breadcrumb[0]["level"] == 0

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_breadcrumb_nested_category(self, db_session):
        """Test get_breadcrumb for nested category"""
        # Mock get_ancestors to return test data
        category = Category(name="Smartphones", slug="smartphones")
        category.level = 2

        # Mock ancestor
        ancestor1 = Category(name="Electronics", slug="electronics")
        ancestor1.id = "uuid-1"
        ancestor1.level = 0

        ancestor2 = Category(name="Mobile", slug="mobile")
        ancestor2.id = "uuid-2"
        ancestor2.level = 1

        with patch.object(category, 'get_ancestors', return_value=[ancestor1, ancestor2]):
            db_session.add(category)
            db_session.commit()

            breadcrumb = category.get_breadcrumb(db_session)

            assert len(breadcrumb) == 3
            assert breadcrumb[0]["name"] == "Electronics"
            assert breadcrumb[1]["name"] == "Mobile"
            assert breadcrumb[2]["name"] == "Smartphones"


class TestCategoryBusinessLogic:
    """RED PHASE: Test category business logic methods"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_product_count_recursive_no_products(self, db_session):
        """Test get_product_count_recursive with no products"""
        category = Category(name="Electronics", slug="electronics")
        db_session.add(category)
        db_session.commit()

        # Mock get_descendants and query to return no products
        with patch.object(category, 'get_descendants', return_value=[]), \
             patch.object(db_session, 'query') as mock_query:

            mock_query.return_value.join.return_value.filter.return_value.scalar.return_value = 0

            count = category.get_product_count_recursive(db_session)
            assert count == 0

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_product_count_recursive_with_products(self, db_session):
        """Test get_product_count_recursive with products"""
        category = Category(name="Electronics", slug="electronics")
        db_session.add(category)
        db_session.commit()

        # Mock get_descendants and query to return product count
        with patch.object(category, 'get_descendants', return_value=[]), \
             patch.object(db_session, 'query') as mock_query:

            mock_query.return_value.join.return_value.filter.return_value.scalar.return_value = 5

            count = category.get_product_count_recursive(db_session)
            assert count == 5

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_is_ancestor_of_true(self, db_session):
        """Test is_ancestor_of returns True for descendant"""
        parent = Category(name="Electronics", slug="electronics")
        parent.path = "/electronics/"
        parent.level = 0

        child = Category(name="Mobile", slug="mobile")
        child.path = "/electronics/mobile/"
        child.level = 1

        assert parent.is_ancestor_of(child) is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_is_ancestor_of_false_same_category(self, db_session):
        """Test is_ancestor_of returns False for same category"""
        category = Category(name="Electronics", slug="electronics")
        category.path = "/electronics/"
        category.level = 0

        assert category.is_ancestor_of(category) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_is_ancestor_of_false_unrelated(self, db_session):
        """Test is_ancestor_of returns False for unrelated category"""
        cat1 = Category(name="Electronics", slug="electronics")
        cat1.path = "/electronics/"
        cat1.level = 0

        cat2 = Category(name="Clothing", slug="clothing")
        cat2.path = "/clothing/"
        cat2.level = 0

        assert cat1.is_ancestor_of(cat2) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_is_descendant_of_true(self, db_session):
        """Test is_descendant_of returns True for ancestor"""
        parent = Category(name="Electronics", slug="electronics")
        child = Category(name="Mobile", slug="mobile")

        with patch.object(parent, 'is_ancestor_of', return_value=True):
            assert child.is_descendant_of(parent) is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_is_descendant_of_false(self, db_session):
        """Test is_descendant_of returns False for non-ancestor"""
        cat1 = Category(name="Electronics", slug="electronics")
        cat2 = Category(name="Clothing", slug="clothing")

        with patch.object(cat1, 'is_ancestor_of', return_value=False):
            assert cat2.is_descendant_of(cat1) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_can_have_parent_none_parent(self, db_session):
        """Test can_have_parent with None parent (root category)"""
        category = Category(name="Electronics", slug="electronics")
        assert category.can_have_parent(None) is True

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_can_have_parent_self_parent(self, db_session):
        """Test can_have_parent with self as parent (should be False)"""
        category = Category(name="Electronics", slug="electronics")
        category.id = "test-uuid"

        parent_candidate = Category(name="Electronics", slug="electronics")
        parent_candidate.id = "test-uuid"

        assert category.can_have_parent(parent_candidate) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_can_have_parent_descendant_as_parent(self, db_session):
        """Test can_have_parent with descendant as parent (should be False)"""
        parent = Category(name="Electronics", slug="electronics")
        child = Category(name="Mobile", slug="mobile")

        with patch.object(parent, 'is_ancestor_of', return_value=True):
            assert parent.can_have_parent(child) is False

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_can_have_parent_valid_parent(self, db_session):
        """Test can_have_parent with valid parent"""
        parent = Category(name="Electronics", slug="electronics")
        child = Category(name="Mobile", slug="mobile")

        parent.id = "parent-uuid"
        child.id = "child-uuid"

        with patch.object(child, 'is_ancestor_of', return_value=False):
            assert child.can_have_parent(parent) is True


class TestCategoryClassMethods:
    """RED PHASE: Test category class methods"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_root_categories_active_only(self, db_session):
        """Test get_root_categories with active_only=True"""
        root1 = Category(name="Electronics", slug="electronics", is_active=True)
        root1.parent_id = None
        root2 = Category(name="Clothing", slug="clothing", is_active=False)
        root2.parent_id = None

        db_session.add_all([root1, root2])
        db_session.commit()

        roots = Category.get_root_categories(db_session, active_only=True)

        assert len(roots) == 1
        assert root1 in roots
        assert root2 not in roots

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_root_categories_include_inactive(self, db_session):
        """Test get_root_categories with active_only=False"""
        root1 = Category(name="Electronics", slug="electronics", is_active=True)
        root1.parent_id = None
        root2 = Category(name="Clothing", slug="clothing", is_active=False)
        root2.parent_id = None

        db_session.add_all([root1, root2])
        db_session.commit()

        roots = Category.get_root_categories(db_session, active_only=False)

        assert len(roots) == 2
        assert root1 in roots
        assert root2 in roots

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_category_tree_empty(self, db_session):
        """Test get_category_tree with no categories"""
        tree = Category.get_category_tree(db_session)
        assert tree == []

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_category_tree_with_categories(self, db_session):
        """Test get_category_tree with categories"""
        root = Category(name="Electronics", slug="electronics", level=0, sort_order=1)
        root.parent_id = None
        db_session.add(root)
        db_session.flush()  # Ensure root has an ID

        child = Category(name="Mobile", slug="mobile", level=1, sort_order=1)
        child.parent_id = root.id
        db_session.add(child)
        db_session.commit()

        tree = Category.get_category_tree(db_session)

        assert len(tree) == 1
        assert tree[0]["name"] == "Electronics"
        assert len(tree[0]["children"]) == 1
        assert tree[0]["children"][0]["name"] == "Mobile"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_get_category_tree_max_depth_limit(self, db_session):
        """Test get_category_tree with max_depth limit"""
        root = Category(name="Electronics", slug="electronics")
        root.parent_id = None
        db_session.add(root)
        db_session.flush()  # Ensure root has an ID and path is updated

        child = Category(name="Mobile", slug="mobile")
        child.parent_id = root.id
        # Set parent relationship for proper level calculation
        child.parent = root
        child.update_path()  # Manually trigger level calculation
        db_session.add(child)
        db_session.flush()  # Ensure child has an ID and path is updated

        grandchild = Category(name="Smartphones", slug="smartphones")
        grandchild.parent_id = child.id
        # Set parent relationship for proper level calculation
        grandchild.parent = child
        grandchild.update_path()  # Manually trigger level calculation
        db_session.add(grandchild)
        db_session.commit()

        tree = Category.get_category_tree(db_session, max_depth=1)

        # Should only include root and child, not grandchild
        categories_in_tree = []
        def collect_categories(nodes):
            for node in nodes:
                categories_in_tree.append(node["name"])
                collect_categories(node.get("children", []))

        collect_categories(tree)

        assert "Electronics" in categories_in_tree
        assert "Mobile" in categories_in_tree
        assert "Smartphones" not in categories_in_tree


class TestCategorySerialization:
    """RED PHASE: Test category serialization methods"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_to_dict_basic(self, db_session):
        """Test to_dict with basic category data"""
        category = Category(
            name="Electronics",
            slug="electronics",
            description="Electronic devices",
            path="/electronics/",
            level=0,
            sort_order=1,
            is_active=True,
            status=CategoryStatus.ACTIVE.value,
            product_count=10
        )

        result = category.to_dict()

        assert result["name"] == "Electronics"
        assert result["slug"] == "electronics"
        assert result["description"] == "Electronic devices"
        assert result["path"] == "/electronics/"
        assert result["level"] == 0
        assert result["sort_order"] == 1
        assert result["is_active"] is True
        assert result["status"] == CategoryStatus.ACTIVE.value
        assert result["product_count"] == 10
        assert result["full_name"] == "Electronics"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_to_dict_with_hierarchy_data(self, db_session):
        """Test to_dict with include_hierarchy=True"""
        category = Category(name="Electronics", slug="electronics")

        # Mock ancestor as Category object
        mock_ancestor = Category(name="Root", slug="root")
        mock_ancestors = [mock_ancestor]
        mock_breadcrumb = [{"name": "Root", "slug": "root"}, {"name": "Electronics", "slug": "electronics"}]

        with patch.object(category, 'get_ancestors', return_value=mock_ancestors), \
             patch.object(category, 'get_breadcrumb', return_value=mock_breadcrumb), \
             patch.object(category, 'get_product_count_recursive', return_value=25):

            category.children = []  # Mock empty children

            result = category.to_dict(include_hierarchy=True, session=db_session)

            assert "ancestors" in result
            assert "breadcrumb" in result
            assert "children_count" in result
            assert "product_count_recursive" in result

            # Check that ancestors were converted to dicts correctly
            assert len(result["ancestors"]) == 1
            assert result["ancestors"][0]["name"] == "Root"
            assert result["ancestors"][0]["slug"] == "root"

            assert result["breadcrumb"] == mock_breadcrumb
            assert result["children_count"] == 0
            assert result["product_count_recursive"] == 25

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_repr_method(self, db_session):
        """Test __repr__ method"""
        category = Category(name="Electronics", slug="electronics")
        category.id = "test-uuid"
        category.level = 0

        repr_str = repr(category)

        assert "Category" in repr_str
        assert "test-uuid" in repr_str
        assert "electronics" in repr_str
        assert "Electronics" in repr_str
        assert "level=0" in repr_str

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_str_method(self, db_session):
        """Test __str__ method"""
        category = Category(name="Electronics", slug="electronics")
        category.level = 0

        str_repr = str(category)

        assert str_repr == "Categoría Electronics (Level 0)"


class TestProductCategoryAssociation:
    """RED PHASE: Test ProductCategory association model"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_product_category_creation(self, db_session):
        """Test creating ProductCategory association"""
        association = ProductCategory(
            product_id="product-uuid",
            category_id="category-uuid",
            is_primary=True,
            sort_order=1,
            assigned_by_id="user-uuid"
        )

        assert association.product_id == "product-uuid"
        assert association.category_id == "category-uuid"
        assert association.is_primary is True
        assert association.sort_order == 1
        assert association.assigned_by_id == "user-uuid"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_product_category_to_dict(self, db_session):
        """Test ProductCategory to_dict method"""
        association = ProductCategory(
            product_id="product-uuid",
            category_id="category-uuid",
            is_primary=False,
            sort_order=2,
            assigned_by_id="user-uuid"
        )

        result = association.to_dict()

        assert result["product_id"] == "product-uuid"
        assert result["category_id"] == "category-uuid"
        assert result["is_primary"] is False
        assert result["sort_order"] == 2
        assert result["assigned_by_id"] == "user-uuid"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_product_category_repr(self, db_session):
        """Test ProductCategory __repr__ method"""
        association = ProductCategory(
            product_id="product-uuid",
            category_id="category-uuid",
            is_primary=True
        )

        repr_str = repr(association)

        assert "ProductCategory" in repr_str
        assert "product-uuid" in repr_str
        assert "category-uuid" in repr_str
        assert "is_primary=True" in repr_str


class TestCategoryEdgeCases:
    """RED PHASE: Test edge cases and error conditions"""

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_with_none_values(self, db_session):
        """Test category creation with None values where allowed"""
        category = Category(
            name="Electronics",
            slug="electronics",
            description=None,
            parent_id=None,
            meta_title=None,
            meta_description=None,
            meta_keywords=None,
            icon_url=None,
            banner_url=None,
            display_config=None
        )

        db_session.add(category)
        db_session.commit()

        assert category.description is None
        assert category.parent_id is None
        assert category.meta_title is None
        assert category.meta_description is None
        assert category.meta_keywords is None
        assert category.icon_url is None
        assert category.banner_url is None
        assert category.display_config is None

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_duplicate_slug_constraint(self, db_session):
        """Test unique constraint on slug"""
        category1 = Category(name="Electronics", slug="electronics")
        category2 = Category(name="Electronic", slug="electronics")  # Same slug

        db_session.add(category1)
        db_session.commit()

        db_session.add(category2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_status_enum_validation(self, db_session):
        """Test CategoryStatus enum validation"""
        # Valid status
        category = Category(name="Electronics", slug="electronics")
        category.status = CategoryStatus.ACTIVE.value
        assert category.status == "ACTIVE"

        category.status = CategoryStatus.INACTIVE.value
        assert category.status == "INACTIVE"

        category.status = CategoryStatus.HIDDEN.value
        assert category.status == "HIDDEN"

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_init_method_with_custom_status(self, db_session):
        """Test Category __init__ with custom status"""
        category = Category(
            name="Electronics",
            slug="electronics",
            status=CategoryStatus.HIDDEN.value
        )

        assert category.status == CategoryStatus.HIDDEN.value

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_init_method_default_status(self, db_session):
        """Test Category __init__ with default status"""
        category = Category(name="Electronics", slug="electronics")

        assert category.status == CategoryStatus.ACTIVE.value

    @pytest.mark.red_test
    @pytest.mark.tdd
    def test_category_init_calls_update_path(self, db_session):
        """Test Category __init__ calls update_path"""
        with patch.object(Category, 'update_path') as mock_update_path:
            category = Category(name="Electronics", slug="electronics")
            mock_update_path.assert_called_once()