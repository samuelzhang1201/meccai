#!/usr/bin/env python3
"""
Launch the Gradio UI for testing the fixed layout.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


def main():
    """Launch the UI for testing."""
    print("🚀 Launching Gradio UI for testing...")
    print("The UI should now show:")
    print("✅ Agent selector dropdown at the top")
    print("✅ Chat input box at the bottom")
    print("✅ Thinking process panel on the right")
    print("\nLaunching on http://localhost:7860")
    print("Press Ctrl+C to stop")
    
    app = GradioBedrockApp()
    app.launch(
        server_port=7860,
        share=False,
        debug=True,
        quiet=False
    )


if __name__ == "__main__":
    main()