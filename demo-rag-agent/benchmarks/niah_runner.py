"""Needle In A Haystack (NIAH) Benchmark Runner.

Tests retrieval recall and extraction precision by injecting synthetic needle
facts at varying depths (10%, 50%, 90%) into a large corpus of distractor documentation.
"""

import os
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import RAGAgent

# Sample distractor background text
DISTRACTOR_PARAGRAPH = """
Kubernetes cluster auto-scaling leverages the Cluster Autoscaler (CA) component paired with Karpenter 
node provisioning. Node groups are partitioned into spot and on-demand instances across three availability 
zones to optimize cost while maintaining high availability SLAs. The cluster ingress controller manages 
traffic distribution with weighted round-robin algorithms, ensuring smooth canary deployments and zero-downtime 
upgrades. Prometheus metrics collectors scrape endpoint telemetry at 15-second intervals, aggregating memory 
utilization, CPU throttling, and network I/O throughput to dynamic Grafana dashboards.
"""


def run_niah_benchmark():
    print("=================================================================")
    print("🧪 Running Needle In A Haystack (NIAH) Retrieval Benchmark")
    print("=================================================================\n")

    agent = RAGAgent()

    test_needles = [
        {
            "depth_pct": 10,
            "secret_code": "TITAN-ALPHA-8842",
            "needle_sentence": "The emergency database encryption override key is TITAN-ALPHA-8842.",
            "query": "What is the emergency database encryption override key?",
        },
        {
            "depth_pct": 50,
            "secret_code": "NEBULA-7091-SEC",
            "needle_sentence": "The secondary disaster recovery staging token is NEBULA-7091-SEC.",
            "query": "What is the secondary disaster recovery staging token?",
        },
        {
            "depth_pct": 90,
            "secret_code": "VORTEX-9921-CORE",
            "needle_sentence": "The root maintenance bypass passcode is VORTEX-9921-CORE.",
            "query": "What is the root maintenance bypass passcode?",
        },
    ]

    results = []

    for test in test_needles:
        depth = test["depth_pct"]
        secret = test["secret_code"]
        query = test["query"]

        print(f"▶ Testing Depth {depth}%...")

        # Construct a synthetic 5,000-word distractor document
        total_blocks = 20
        needle_position = int((depth / 100.0) * total_blocks)
        
        doc_blocks = []
        for i in range(total_blocks):
            if i == needle_position:
                doc_blocks.append(f"\n## Emergency Protocol Section {i+1}\n{test['needle_sentence']}\n")
            else:
                doc_blocks.append(f"\n## Infrastructure Subsystem Section {i+1}\n{DISTRACTOR_PARAGRAPH}\n")

        synthetic_doc = "\n".join(doc_blocks)

        # Inject into agent's search engine
        doc_id = f"synthetic_haystack_{depth}pct"
        agent.engine.add_document(doc_id=doc_id, content=synthetic_doc, filename=f"{doc_id}.md")
        agent.engine._build_index()

        # Run query
        start_time = time.time()
        response = agent.ask(query)
        latency = time.time() - start_time

        answer = response["answer"]
        retrieved_ids = [c["doc_id"] for c in response["retrieved_evidence"]]

        # Verify
        retrieval_pass = doc_id in retrieved_ids
        extraction_pass = secret in answer

        status = "PASSED" if (retrieval_pass and extraction_pass) else "FAILED"
        print(f"  • Retrieval Found Target: {'✅' if retrieval_pass else '❌'}")
        print(f"  • Extracted Secret Code:  {'✅' if extraction_pass else '❌'}")
        print(f"  • Latency: {latency:.2f}s | Status: {status}")
        print(f"  • Answer: {answer.strip()[:140]}...\n")

        results.append(
            {
                "depth": depth,
                "secret": secret,
                "retrieval_pass": retrieval_pass,
                "extraction_pass": extraction_pass,
                "passed": retrieval_pass and extraction_pass,
            }
        )

    # Summary Table
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    score = (passed / total) * 100.0

    print("=================================================================")
    print(f"🏁 NIAH Benchmark Results: {passed}/{total} Passed ({score:.1f}%)")
    print("=================================================================")
    for r in results:
        print(f"Depth {r['depth']:2d}%: [{'PASS' if r['passed'] else 'FAIL'}]")


if __name__ == "__main__":
    run_niah_benchmark()
