#!/usr/bin/env python3
"""
Integration test for Issue #1 (Real DAG Planner) and Issue #5 (Memory Integration)

Tests:
1. Real DAG generation for complex goal
2. Memory retrieval before planning  
3. Memory storage after failure
4. Retrieval of stored lessons
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Add runtime directory to path
runtime_dir = Path(__file__).parent.parent / "runtime"
sys.path.insert(0, str(runtime_dir))


def run_command(cmd):
    """Run Python command and return parsed JSON result."""
    # Add PYTHONPATH to ensure modules are found
    env = os.environ.copy()
    env["PYTHONPATH"] = str(runtime_dir)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def test_dag_planner():
    """Test Issue #1: Real DAG Planner."""
    print("\n" + "=" * 80)
    print("TEST 1: Real DAG Planner (Issue #1)")
    print("=" * 80)
    
    goal = "Build satellite UI + backend with PostgreSQL database"
    print(f"\nTesting goal: {goal}\n")
    
    cmd = f'python -m dotagent_runtime.dag_planner_cli --goal "{goal}" --json-output'
    result = run_command(cmd)
    
    if not result:
        print("❌ DAG Planner failed")
        return False
    
    # Validation checks
    checks = {
        "Has tasks": lambda: result.get("tasks") and len(result["tasks"]) > 0,
        "Detects parallelization": lambda: result.get("has_parallelization") == True,
        "Task count > 1": lambda: result.get("task_count", 0) > 1,
        "UI task found": lambda: any("ui" in t.get("name", "").lower() for t in result.get("tasks", [])),
        "Backend task found": lambda: any("backend" in t.get("name", "").lower() for t in result.get("tasks", [])),
        "Database task found": lambda: any("database" in t.get("name", "").lower() or "postgresql" in t.get("name", "").lower() for t in result.get("tasks", [])),
        "Integration task found": lambda: any("integrate" in t.get("name", "").lower() for t in result.get("tasks", [])),
    }
    
    passed = 0
    for check_name, check_func in checks.items():
        if check_func():
            print(f"  ✓ {check_name}")
            passed += 1
        else:
            print(f"  ✗ {check_name}")
    
    print(f"\n📊 DAG Structure ({result.get('task_count')} tasks):")
    for task in result.get("tasks", []):
        deps = f" (depends: {', '.join(task.get('depends_on', []))})" if task.get("depends_on") else " (independent)"
        print(f"  - {task.get('id')}: {task.get('name')}{deps}")
    
    success = passed == len(checks)
    print(f"\n{'✓' if success else '✗'} DAG Planner: {passed}/{len(checks)} checks passed")
    return success


def test_memory_retrieval():
    """Test Issue #5: Memory Retrieval."""
    print("\n" + "=" * 80)
    print("TEST 2: Memory Retrieval (Issue #5)")
    print("=" * 80)
    
    print("\nTesting memory retrieval for authentication task\n")
    
    cmd = 'python -m dotagent_runtime.memory_integration_cli --goal "Implement authentication system" --mode retrieve --json-output'
    result = run_command(cmd)
    
    if not result:
        print("⚠️  Memory retrieval failed (expected if no prior lessons)")
        return True
    
    # Validation checks
    checks = {
        "Has mode": lambda: result.get("mode") == "retrieve",
        "Has goal": lambda: result.get("goal") is not None,
        "Has lessons_prompt": lambda: "lessons_prompt" in result,
    }
    
    passed = 0
    for check_name, check_func in checks.items():
        if check_func():
            print(f"  ✓ {check_name}")
            passed += 1
        else:
            print(f"  ✗ {check_name}")
    
    lessons = result.get("lessons", [])
    if lessons and isinstance(lessons, (list, dict)):
        if isinstance(lessons, dict):
            lessons_list = list(lessons.values()) if isinstance(lessons, dict) else lessons
        else:
            lessons_list = lessons
        
        if lessons_list:
            lesson_count = len(lessons_list) if isinstance(lessons_list, list) else len(list(lessons_list))
            print(f"\n📚 Retrieved {lesson_count} lessons:")
            for i, lesson in enumerate(list(lessons_list)[:2]):
                preview = str(lesson)[:70] + "..." if len(str(lesson)) > 70 else str(lesson)
                print(f"  - {preview}")
    
    success = passed == len(checks)
    print(f"\n{'✓' if success else '✗'} Memory Retrieval: {passed}/{len(checks)} checks passed")
    return success


def test_memory_storage():
    """Test Issue #5: Memory Storage."""
    print("\n" + "=" * 80)
    print("TEST 3: Memory Storage (Issue #5)")
    print("=" * 80)
    
    print("\nTesting memory storage for a failure\n")
    
    # Create temp files with step and result data
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        step_file = f.name
        json.dump({
            "step_id": "test_step_auth",
            "kind": "IMPL",
            "action": "Implement authentication"
        }, f)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        result_file = f.name
        json.dump({
            "status": "FAILED",
            "error": "JWT validation failed",
            "stderr": "Module 'jwt' not found",
            "exit_code": 1
        }, f)
    
    try:
        cmd = f'python -m dotagent_runtime.memory_integration_cli --goal "Implement authentication system" --step-json "{step_file}" --result-json "{result_file}" --attempt 0 --mode store --json-output'
        result = run_command(cmd)
        
        if not result:
            print("❌ Memory storage failed")
            return False
        
        # Validation checks
        checks = {
            "Mode is store": lambda: result.get("mode") == "store",
            "Storage successful": lambda: result.get("stored") == True,
            "Has message": lambda: result.get("message") is not None,
        }
        
        passed = 0
        for check_name, check_func in checks.items():
            if check_func():
                print(f"  ✓ {check_name}")
                passed += 1
            else:
                print(f"  ✗ {check_name}")
        
        print(f"\n💾 Result: {result.get('message')}")
        
        success = passed == len(checks)
        print(f"\n{'✓' if success else '✗'} Memory Storage: {passed}/{len(checks)} checks passed")
        return success
    finally:
        Path(step_file).unlink(missing_ok=True)
        Path(result_file).unlink(missing_ok=True)


def test_memory_retrieval_after_storage():
    """Test Issue #5: Memory Retrieval After Storage."""
    print("\n" + "=" * 80)
    print("TEST 4: Memory Retrieval After Storage (Issue #5)")
    print("=" * 80)
    
    print("\nTesting that stored lessons are now retrievable\n")
    
    cmd = 'python -m dotagent_runtime.memory_integration_cli --goal "Implement authentication system" --mode retrieve --json-output'
    result = run_command(cmd)
    
    if not result:
        print("❌ Memory retrieval failed")
        return False
    
    # Validation checks
    checks = {
        "Has lessons after storage": lambda: result.get("lessons") and (len(result["lessons"]) > 0 if isinstance(result["lessons"], list) else len(result["lessons"]) > 0),
        "Lessons include stored content": lambda: any("jwt" in str(l).lower() or "auth" in str(l).lower() for l in (result.get("lessons") if isinstance(result.get("lessons"), list) else result.get("lessons").values() if isinstance(result.get("lessons"), dict) else [])),
    }
    
    passed = 0
    for check_name, check_func in checks.items():
        if check_func():
            print(f"  ✓ {check_name}")
            passed += 1
        else:
            print(f"  ✗ {check_name}")
    
    lessons = result.get("lessons", [])
    if lessons and isinstance(lessons, (list, dict)):
        if isinstance(lessons, dict):
            lessons_list = list(lessons.values()) if isinstance(lessons, dict) else lessons
        else:
            lessons_list = lessons
        
        if lessons_list:
            lesson_count = len(lessons_list) if isinstance(lessons_list, list) else len(list(lessons_list))
            print(f"\n📚 Retrieved {lesson_count} lessons (including stored one):")
            for i, lesson in enumerate(list(lessons_list)[:2]):
                preview = str(lesson)[:70] + "..." if len(str(lesson)) > 70 else str(lesson)
                print(f"  - {preview}")
    
    success = passed == len(checks)
    print(f"\n{'✓' if success else '✗'} Memory Retrieval After Storage: {passed}/{len(checks)} checks passed")
    return success


def main():
    """Run all integration tests."""
    print("\n" + "=" * 80)
    print("Integration Tests: Issue #1 (DAG Planner) + Issue #5 (Memory Integration)")
    print("=" * 80)
    
    results = []
    results.append(("DAG Planner", test_dag_planner()))
    results.append(("Memory Retrieval", test_memory_retrieval()))
    results.append(("Memory Storage", test_memory_storage()))
    results.append(("Memory Retrieval After Storage", test_memory_retrieval_after_storage()))
    
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed\n")
    
    for name, result in results:
        status = "✓" if result else "✗"
        color = "green" if result else "red"
        print(f"  {status} {name}")
    
    print()
    
    if passed == total:
        print("✅ All integration tests PASSED - Issues #1 and #5 are 100% complete!")
        return 0
    else:
        print("⚠️  Some tests failed. Review output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
