#!/usr/bin/env python3
"""
Final Comprehensive System Verification
"""
import asyncio
import json
import urllib.request
import os

async def test_all():
    print("=" * 70)
    print("FINAL COMPREHENSIVE SYSTEM VERIFICATION")
    print("=" * 70)

    # Set environment
    os.environ['SEARCH_ENGINE_SERVER_URL'] = 'http://localhost:8000'

    tests_passed = 0
    tests_failed = 0

    # Test 1: Google Search
    print("\n[1/6] Testing Google Search...")
    try:
        url = 'http://localhost:8000/api/search'
        data = json.dumps({"query": "Kubernetes tutorial", "max_results": 3}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            assert result['success'] == True
            assert result['provider'] == 'google'
            assert result['results_count'] == 3
            print(f"  ✓ PASS: Google search working (Provider: {result['provider']}, Results: {result['results_count']}, Remaining: {result['remaining_quota']})")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Test 2: Brave Search
    print("\n[2/6] Testing Brave Search...")
    try:
        url = 'http://localhost:8000/api/search'
        data = json.dumps({"query": "Docker tutorial", "provider": "brave"}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            assert result['success'] == True
            assert result['provider'] == 'brave'
            print(f"  ✓ PASS: Brave search working (Provider: {result['provider']}, Results: {result['results_count']})")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Test 3: Serper Search
    print("\n[3/6] Testing Serper Search...")
    try:
        url = 'http://localhost:8000/api/search'
        data = json.dumps({"query": "Microservices", "provider": "serper"}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            assert result['success'] == True
            assert result['provider'] == 'serper'
            print(f"  ✓ PASS: Serper search working (Provider: {result['provider']}, Results: {result['results_count']})")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Test 4: Python Integration
    print("\n[4/6] Testing Python Integration...")
    try:
        from skill_loader import SkillLoader
        loader = SkillLoader('/mnt/c/Project/Aethercore/skills_config.json')
        result = await loader.execute_tool(
            'AetherCore.SearchEngine',
            'search',
            {'query': 'Python async programming', 'max_results': 2},
            {'context_id': 'final-test'}
        )
        assert result['success'] == True
        assert 'results' in result
        print(f"  ✓ PASS: Python integration working (Provider: {result['provider']}, Results: {result['results_count']})")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Test 5: Scraping
    print("\n[5/6] Testing Web Scraping...")
    try:
        url = 'http://localhost:8000/api/scrape'
        data = json.dumps({"url": "https://example.com", "render_js": False}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            assert result['success'] == True
            assert 'content' in result
            assert len(result['content']) > 0
            print(f"  ✓ PASS: Scraping working (Provider: {result['provider']}, Content length: {len(result['content'])} chars)")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Test 6: Quota Reset
    print("\n[6/6] Testing Quota Reset...")
    try:
        url = 'http://localhost:8000/api/reset-quotas'
        data = json.dumps({"provider": "google"}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            assert result['success'] == True
            assert 'reset' in result['message'].lower()
            print(f"  ✓ PASS: Quota reset working ({result['message']})")
            tests_passed += 1
    except Exception as e:
        print(f"  ✗ FAIL: {str(e)}")
        tests_failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}/6")
    print(f"Tests Failed: {tests_failed}/6")
    print(f"Success Rate: {(tests_passed/6)*100:.1f}%")
    print("=" * 70)

    if tests_failed == 0:
        print("\n🎉 ALL SYSTEMS OPERATIONAL - READY FOR PRODUCTION! 🎉")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed - review needed")

    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_all())
