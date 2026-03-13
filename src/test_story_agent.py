import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from agents.story_agent import StoryAgent

def main():
    agent = StoryAgent()
    story = "In a world where shadows can be captured in jars, a young glassblower accidentally traps the shadow of a forgotten god."
    print(f"--- Running {agent.name} ---")
    result = agent.run(story)
    
    print("\nNarrative Beats:")
    for beat in result['beats']:
        print(f"[{beat['id']}] {beat['mood']}: {beat['description']}")
    
    print(f"\nMetadata: {result['metadata']}")

if __name__ == "__main__":
    main()
