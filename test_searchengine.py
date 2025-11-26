#!/usr/bin/env python3
"""
Test script for SearchEngine integration
"""
import sys
import os
import asyncio
import json
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, '/mnt/c/Project/Aethercore')

from skill_loader import SkillLoader

async def test_search():
    print("=" * 60)
    print("Testing SearchEngine Integration")
    print("=" * 60)

    # Set environment variables
    os.environ['SEARCH_ENGINE_SERVER_URL'] = 'http://localhost:8000'

    # Initialize skill loader
    loader = SkillLoader('/mnt/c/Project/Aethercore/skills_config.json')

    print("\n1. Testing Search Tool...")
    print("-" * 60)
    result = await loader.execute_tool(
        skill_name="AetherCore.SearchEngine",
        tool_name="search",
        parameters={
            "query": "Python async programming tutorial",
            "max_results": 5,
            "provider": "auto"
        },
        context={"context_id": "test-123"}
    )

    print(f"Success: {result.get('success')}")
    if result.get('success'):
        print(f"Provider: {result.get('provider')}")
        print(f"Query: {result.get('query')}")
        print(f"Results Count: {result.get('results_count')}")
        print(f"Execution Time: {result.get('execution_time_ms')}ms")
        print(f"\nFirst 3 results:")
        for i, r in enumerate(result.get('results', [])[:3], 1):
            print(f"  {i}. {r.get('title')}")
            print(f"     URL: {r.get('url')}")
            print(f"     Snippet: {r.get('snippet', '')[:100]}...")
    else:
        print(f"Error: {result.get('error')}")

    print("\n2. Testing Quota Status...")
    print("-" * 60)
    quota_result = await loader.execute_tool(
        skill_name="AetherCore.SearchEngine",
        tool_name="quota_status",
        parameters={},
        context={"context_id": "test-123"}
    )
    print(f"Success: {quota_result.get('success')}")
    print(f"Status: {quota_result}")

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_search())
