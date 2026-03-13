# Creator: Anime Sequence Maker

Creator is a creative-director-style system that orchestrates the creation of anime-style animated sequences using Gemini 3 and specialized agents.

## Project Structure
- `src/agents/`: Individual agent logic (Story, Storyboard, etc.).
- - `src/utils/`: Wrappers for Google Cloud Services (GCS, GenAI SDK).
  - - `data/`: Local storage for assets and intermediate data.
   
    - ## Setup
    - 1. Install dependencies: `pip install -r requirements.txt`
      2. 2. Authenticate with Google Cloud: `gcloud auth application-default login`
         3. 3. Configure environment variables for project IDs and GCS buckets.
