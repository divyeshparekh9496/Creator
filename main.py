#!/usr/bin/env python3
"""
Creator CLI — convert stories into anime sequences.

Usage:
    python main.py --story "Your story text here"
    python main.py --file story.txt
    python main.py --file story.txt --output data/my_anime
"""
import argparse
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import CreatorPipeline
from src.config import DEFAULT_OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(
        description="Creator — AI Anime Sequence Maker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --story "A lone samurai walks through cherry blossoms"
  python main.py --file my_story.txt --output data/samurai_anime
        """,
    )
    parser.add_argument(
        "--story", "-s", type=str, help="Story text to convert into anime"
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Path to a text file containing the story"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})"
    )
    parser.add_argument(
        "--api-key", type=str, default=None,
        help="Google API key (overrides .env)"
    )

    args = parser.parse_args()

    # Get story text
    story_text = None
    if args.story:
        story_text = args.story
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r") as f:
            story_text = f.read()
    else:
        print("Error: Provide --story or --file")
        parser.print_help()
        sys.exit(1)

    if not story_text or not story_text.strip():
        print("Error: Story text is empty")
        sys.exit(1)

    # Run pipeline
    print(f"\n🎬 Creator — Starting anime generation...")
    print(f"   Story: {story_text[:80]}{'...' if len(story_text) > 80 else ''}")
    print(f"   Output: {args.output}\n")

    pipeline = CreatorPipeline(
        api_key=args.api_key,
        output_dir=args.output,
    )

    result = pipeline.run_full(story_text)

    # Summary
    print("\n📋 Output Summary:")
    print(f"   Story:      {result.get('story_analysis', {}).get('title', 'N/A')}")
    print(f"   Scenes:     {len(result.get('storyboard', {}).get('scenes', []))}")
    print(f"   Characters: {len(result.get('character_data', {}).get('character_sheets', []))}")
    print(f"   Keyframes:  {len(result.get('keyframes', {}).get('keyframes', []))}")
    final = result.get("final_assembly", {})
    print(f"   Parts:      {len(final.get('rendered_parts', []))}")
    print(f"   Final:      {final.get('final_episode', 'N/A')}")
    print(f"\n   All outputs in: {args.output}/")


if __name__ == "__main__":
    main()
