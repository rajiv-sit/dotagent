from __future__ import annotations
from typing import Dict, Any, List
from .utils import sha256_text

def build_evidence_bundle(job: Dict[str, Any], plan: Dict[str, Any], outputs: List[Dict[str, Any]], validation: Dict[str, Any]) -> Dict[str, Any]:
    payload = {
        "job": job,
        "plan": plan,
        "outputs": outputs,
        "validation": validation,
    }
    import json
    canonical = json.dumps(payload, sort_keys=True)
    return {
        **payload,
        "sha256": sha256_text(canonical)
    }
