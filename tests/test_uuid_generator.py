"""
Test Suite for UUID Generator
"""

import pytest
from tools.core.uuid_generator import UUIDGenerator


class TestUUIDGeneration:
    """Test UUID generation functionality"""

    def test_uuid_length(self):
        """UUID should be exactly 12 characters"""
        gen = UUIDGenerator()
        uuid = gen.generate()
        assert len(uuid) == 12

    def test_uuid_is_hex(self):
        """UUID should be valid hexadecimal"""
        gen = UUIDGenerator()
        uuid = gen.generate()
        assert all(c in '0123456789abcdef' for c in uuid)

    def test_uuid_uniqueness(self):
        """Generated UUIDs should be unique"""
        gen = UUIDGenerator()
        uuids = [gen.generate() for _ in range(100)]
        assert len(uuids) == len(set(uuids))

    def test_collision_detection(self):
        """Collision detection should prevent duplicates"""
        gen = UUIDGenerator()
        uuid1 = gen.generate()
        # Manually add to existing
        gen.existing_ids.add(uuid1)
        uuid2 = gen.generate()
        assert uuid1 != uuid2

    def test_uuid_validation(self):
        """UUID validation should work correctly"""
        gen = UUIDGenerator()
        uuid = gen.generate()
        assert gen.validate_uuid(uuid)

    def test_invalid_uuid_validation(self):
        """Invalid UUIDs should fail validation"""
        gen = UUIDGenerator()
        assert not gen.validate_uuid("invalid")
        assert not gen.validate_uuid("")
        assert not gen.validate_uuid("1234567890")  # Too short
        assert not gen.validate_uuid("gggggggggggg")  # Invalid hex

    def test_collision_duplicate(self):
        """Validation should reject duplicates"""
        gen = UUIDGenerator()
        uuid1 = gen.generate()
        gen.existing_ids.add(uuid1)
        assert not gen.validate_uuid(uuid1)

    def test_load_existing_ids(self):
        """Should be able to load existing IDs from metadata"""
        gen = UUIDGenerator()
        # This will load from actual files if they exist
        existing = gen.load_existing_ids(gen.existing_ids)
        assert isinstance(existing, set)
