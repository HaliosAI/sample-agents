"""Grounded QA & Faithfulness Benchmark Evaluator.

Evaluates:
1. Factual Correctness against ground truth
2. Citation Attribution (presence of valid [Doc: ...] citations)
3. Honest Refusal on out-of-domain questions
4. Conflict Resolution (superseded v1 vs active v2 policy)
"""

import os
import re
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import RAGAgent

TEST_CASES = [
    {
        "category": "Architecture Fact Recall",
        "question": "What is the maximum asynchronous replication lag threshold for Aurora PostgreSQL read replicas?",
        "expected_fact": "15 milliseconds",
        "expected_doc": "cloud_architecture",
        "type": "grounded_fact",
    },
    {
        "category": "Compliance & Security",
        "question": "What is the mandatory encryption standard at rest, and how often are KMS keys rotated?",
        "expected_fact": "AES-256",
        "expected_doc": "security_compliance",
        "type": "grounded_fact",
    },
    {
        "category": "Conflict Resolution (Policy v1 vs v2)",
        "question": "What is our customer refund eligibility window and restocking fee for standard customers?",
        "expected_fact": "30",
        "expected_doc": "refund_policy_v2_updated",
        "type": "conflict_resolution",
        "anti_pattern": "$15.00 restocking fee",  # v1 fee should not be presented as active
    },
    {
        "category": "Out-of-Domain / Honest Refusal",
        "question": "What is the reimbursement policy for employee business flight upgrades?",
        "expected_fact": "sufficient information",  # Expects refusal
        "type": "honest_refusal",
    },
]


def evaluate_qa_suite():
    print("=================================================================")
    print("📋 Running Grounded QA, Citation & Faithfulness Benchmark")
    print("=================================================================\n")

    agent = RAGAgent()
    results = []

    for idx, test in enumerate(TEST_CASES, 1):
        print(f"Test #{idx} [{test['category']}]")
        print(f"❓ Question: {test['question']}")

        response = agent.ask(test["question"])
        answer = response["answer"]

        # 1. Check Factual Recall / Expected Target
        fact_pass = test["expected_fact"].lower() in answer.lower()

        # 2. Check Citation Attribution
        has_citations = bool(re.search(r"\[Doc:\s*[^\]]+\]", answer))

        # 3. Specific checks per category
        if test["type"] == "honest_refusal":
            # Pass if refusal phrase is triggered and no hallucinations
            passed = "sufficient information" in answer.lower() or "do not have" in answer.lower()
            print(f"  • Honest Refusal: {'✅ PASSED' if passed else '❌ FAILED'}")
        elif test["type"] == "conflict_resolution":
            # Must mention 30 days and not assert the $15 fee as active
            no_anti_pattern = test.get("anti_pattern", "") not in answer
            passed = fact_pass and has_citations and no_anti_pattern
            print(f"  • Active Policy Picked: {'✅' if fact_pass else '❌'}")
            print(f"  • Proper Citations:     {'✅' if has_citations else '❌'}")
            print(f"  • Overall Status:       {'✅ PASSED' if passed else '❌ FAILED'}")
        else:
            passed = fact_pass and has_citations
            print(f"  • Factual Recall:    {'✅' if fact_pass else '❌'} (Expected: '{test['expected_fact']}')")
            print(f"  • Citation Included: {'✅' if has_citations else '❌'}")
            print(f"  • Overall Status:    {'✅ PASSED' if passed else '❌ FAILED'}")

        print(f"  • Answer snippet: {answer.strip()[:140]}...\n")

        results.append(
            {
                "category": test["category"],
                "passed": passed,
                "fact_pass": fact_pass,
                "has_citations": has_citations,
            }
        )

    # Summary Table
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    score = (passed / total) * 100.0

    print("=================================================================")
    print(f"🏁 QA Benchmark Summary: {passed}/{total} Passed ({score:.1f}%)")
    print("=================================================================")
    for r in results:
        print(f"• {r['category']:35s} : [{'PASS' if r['passed'] else 'FAIL'}]")


if __name__ == "__main__":
    evaluate_qa_suite()
