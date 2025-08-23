#!/usr/bin/env python3
"""
Start the fixed Gradio UI.
"""

import sys
from pathlib import Path
import gradio as gr

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from meccaai.apps.gradio_app import GradioBedrockApp


def main():
    """Start the fixed UI."""
    print("🚀 STARTING FIXED GRADIO UI")
    print("=" * 40)
    print("✅ Agent selector at top")
    print("✅ Chat input at bottom") 
    print("✅ Thinking panel on right")
    print("🌐 URL: http://localhost:7860")
    print("=" * 40)
    
    # Kill any existing processes
    import subprocess
    try:
        result = subprocess.run(['lsof', '-ti:7860'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], capture_output=True)
            print(f"🔄 Killed {len(pids)} existing processes")
    except:
        pass
    
    # Start fresh app
    app = GradioBedrockApp()
    
    try:
        app.launch(
            server_port=7860,
            server_name="0.0.0.0", 
            share=False,
            debug=False,
            show_error=True,
            quiet=False
        )
    except KeyboardInterrupt:
        print("\n👋 Gradio UI stopped")


if __name__ == "__main__":
    main()