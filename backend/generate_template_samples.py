#!/usr/bin/env python3
"""Generate sample covers for all templates to showcase the options."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cover_generator import TemplateCoverGenerator


async def main():
    """Generate sample covers for documentation."""
    print("Generating sample covers for all templates...")

    generator = TemplateCoverGenerator()
    templates = generator.get_available_templates()

    samples_dir = Path("docs/samples/covers")
    samples_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for genre, template_ids in templates.items():
        print(f"\n{genre.upper()}:")
        for template_id in template_ids:
            output = await generator.generate(
                title=f"{genre.title()} Song",
                genre=genre,
                template_id=template_id,
                song_id=f"sample_{genre}_{template_id}",
                subtitle="Sample Cover"
            )

            # Move to samples directory
            sample_path = samples_dir / f"{genre}_{template_id}.png"
            output.rename(sample_path)

            print(f"  ✓ {template_id} -> {sample_path.name}")
            count += 1

    print(f"\n✅ Generated {count} sample covers in {samples_dir}")


if __name__ == "__main__":
    asyncio.run(main())
