"""
StorybookAgent — Natively interleaved multimodal storybook generation.

This agent uses Gemini 3.1 Flash Image's native API interleaving to output 
text and generated images in a single stream, creating a Creative Storyteller markdown document.
"""
import os
import uuid
from typing import Dict, Any

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_IMAGE

SYSTEM_PROMPT = """You are a master Creative Storyteller and Illustrator.
Your job is to read the story, the character profiles, and the storyboard, and then 
generate a beautifully formatted, immersive 'Interactive Storybook'.

CRITICAL INSTRUCTION:
You MUST use your native multimodal generation capabilities to interleave text and images.
Write the story narrative, and at key moments, naturally insert an illustration of what is happening.
Do NOT just return text and put placeholders like [Insert Image]. You must generate the ACTUAL images inline in your response stream alongside the text.

Format the text using rich Markdown (headers, italics, blockquotes for dialogue).
Start with a title header, and tell the entire story from beginning to end, weaving your generated illustrations throughout the narrative flow.
"""

class StorybookAgent(BaseAgent):
    """
    Agent 7: Native Interleaved Storybook Generator.
    
    Generates a Markdown file with mixed-media (text + images) using Gemini's response_modalities.
    """

    def __init__(self, output_dir: str = "data/output/storybook", **kwargs):
        super().__init__(name="StorybookAgent", **kwargs)
        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        storyboard = input_data.get("storyboard", {})
        characters = input_data.get("character_data", {})
        story = input_data.get("story_analysis", {})

        self.log("Generating natively interleaved Storybook (Text + Images)...")

        prompt = (
            f"Here is the story analysis:\n{story}\n\n"
            f"Here are the character profiles:\n{characters}\n\n"
            f"Here is the storyboard breakdown:\n{storyboard}\n\n"
            "Please generate the beautifully formatted, interactive Storybook now. Remember to generate actual illustrations inline!"
        )

        # Call the GenAIClient's generate_interleaved method.
        # This returns a list of strings (text) and PIL Images.
        results = self.genai.generate_interleaved(
            prompt=prompt,
            model=MODEL_FLASH_IMAGE, 
            aspect_ratio="16:9" 
        )

        if not results:
            self.log("Failed to generate interleaved storybook.")
            return {"markdown_path": "", "images": [], "error": "Generation failed"}

        markdown_content = ""
        image_paths = []

        # Parse the interleaved results
        for idx, item in enumerate(results):
            if isinstance(item, str):
                markdown_content += item + "\n"
            else:
                # It's a PIL Image
                filename = f"illustration_{uuid.uuid4().hex[:8]}.png"
                img_path = os.path.join(self.images_dir, filename)
                item.save(img_path)
                image_paths.append(img_path)
                
                # Insert the markdown image tag into the text stream
                markdown_content += f"\n\n![Illustration]({filename})\n\n"

        # Save the final markdown storybook
        md_file = os.path.join(self.output_dir, "storybook.md")
        with open(md_file, "w") as f:
            f.write(markdown_content)

        self.log(f"Storybook generated! Saved {len(image_paths)} inline images to {md_file}")

        return {
            "markdown_path": md_file,
            "images": image_paths,
            "text_length": len(markdown_content)
        }
