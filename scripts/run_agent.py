#!/usr/bin/env python3
"""CLI to run the clinical decision support multi-agent."""

import sys
sys.path.insert(0, ".")

from src.agents.graph import create_clinical_graph


def main():
    print("=" * 60)
    print("Clinical Decision Support Multi-Agent")
    print("=" * 60)
    print("\nInitializing graph...")
    
    graph = create_clinical_graph()
    
    print("Ready! Type your query (or 'quit' to exit)\n")
    
    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            
            result = graph.invoke({
                "query": query,
                "route": None,
                "tools_results": [],
                "orgs_results": [],
                "response": "",
                "error": None
            })
            
            print(f"\n[Route: {result.get('route', 'unknown')}]")
            print(f"\nAssistant: {result.get('response', 'No response')}\n")
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
