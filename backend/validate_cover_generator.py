#!/usr/bin/env python3
"""Validation script for cover generator service."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cover_generator import (
    TemplateCoverGenerator,
    get_available_templates,
)


async def main():
    """Validate cover generator functionality."""
    print("=" * 60)
    print("Cover Generator Validation")
    print("=" * 60)

    # Test 1: Check available templates
    print("\n1. Testing get_available_templates()...")
    templates = get_available_templates()
    print(f"   Available genres: {list(templates.keys())}")
    print(f"   Pop templates: {templates.get('pop', [])}")
    print("   ✓ Template listing works")

    # Test 2: Initialize generator
    print("\n2. Testing TemplateCoverGenerator initialization...")
    generator = TemplateCoverGenerator()
    print(f"   Output directory: {generator.output_dir}")
    print(f"   Output size: {generator.OUTPUT_SIZE}")
    print("   ✓ Generator initialized")

    # Test 3: Test hex to RGB conversion
    print("\n3. Testing color conversion...")
    test_cases = [
        ("#FF0000", (255, 0, 0)),
        ("#00FF00", (0, 255, 0)),
        ("#0000FF", (0, 0, 255)),
    ]
    for hex_color, expected in test_cases:
        result = generator._hex_to_rgb(hex_color)
        assert result == expected, f"Expected {expected}, got {result}"
    print("   ✓ Color conversion works")

    # Test 4: Create gradient
    print("\n4. Testing gradient creation...")
    gradient = generator._create_gradient((100, 100), "#FF0000", "#0000FF")
    assert gradient.size == (100, 100), f"Expected (100, 100), got {gradient.size}"
    assert gradient.mode == "RGB", f"Expected RGB mode, got {gradient.mode}"
    print("   ✓ Gradient creation works")

    # Test 5: Generate sample cover
    print("\n5. Testing cover generation...")
    output = await generator.generate(
        title="Test Song",
        genre="pop",
        template_id="gradient_bright",
        song_id="validation_test"
    )
    assert output.exists(), f"Output file not created: {output}"
    print(f"   Output: {output}")
    print("   ✓ Cover generation works")

    # Test 6: Verify image properties
    print("\n6. Verifying generated image...")
    from PIL import Image
    with Image.open(output) as img:
        assert img.size == (1280, 720), f"Expected 1280x720, got {img.size}"
        assert img.mode == "RGB", f"Expected RGB, got {img.mode}"
    print(f"   Size: {img.size}")
    print(f"   Mode: {img.mode}")
    print("   ✓ Image properties correct")

    print("\n" + "=" * 60)
    print("✓ All validation checks passed!")
    print("=" * 60)

    # Cleanup
    if output.exists():
        output.unlink()
        print(f"\nCleaned up test file: {output}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
