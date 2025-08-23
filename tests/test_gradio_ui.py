#!/usr/bin/env python3
"""
Test script to launch the Gradio UI and test the thinking flow display.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


def main():
    """Launch the Gradio app for testing."""
    print("🚀 Starting Gradio UI with improved thinking flow display...")
    print("After the UI loads, try asking a question like:")
    print("   'Show me the tableau users and dbt model execution times'")
    print("This should trigger both tableau and dbt tools and show the thinking process!")
    
    app = GradioBedrockApp()
    app.launch(
        server_name="127.0.0.1",  # Localhost only for testing
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )


if __name__ == "__main__":
    main()