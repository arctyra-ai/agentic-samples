#!/usr/bin/env python3
"""
Week 6: Graph Visualization Utility
Generates visual representations of the LangGraph workflow.
Outputs: PNG image and ASCII text representation.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def visualize_graph():
    """Generate and save graph visualization"""
    try:
        from langgraph_system import graph
    except ImportError as e:
        print(f"Import error: {e}")
        print("Ensure langgraph is installed: pip install langgraph")
        return

    # Try PNG visualization (requires graphviz/mermaid)
    try:
        graph_image = graph.get_graph().draw_mermaid_png()
        output_path = os.path.join(os.path.dirname(__file__), "graph_visualization.png")
        with open(output_path, "wb") as f:
            f.write(graph_image)
        print(f"Graph PNG saved to: {output_path}")
    except Exception as e:
        print(f"PNG generation failed (may need graphviz): {e}")

    # ASCII representation (always works)
    try:
        ascii_graph = graph.get_graph().draw_ascii()
        print("\nASCII Graph Representation:")
        print(ascii_graph)
    except Exception as e:
        print(f"ASCII generation failed: {e}")

    # Mermaid text (always works)
    try:
        mermaid_text = graph.get_graph().draw_mermaid()
        output_path = os.path.join(os.path.dirname(__file__), "graph_visualization.mermaid")
        with open(output_path, "w") as f:
            f.write(mermaid_text)
        print(f"\nMermaid text saved to: {output_path}")
        print("\nMermaid source:")
        print(mermaid_text)
    except Exception as e:
        print(f"Mermaid generation failed: {e}")


if __name__ == "__main__":
    visualize_graph()
