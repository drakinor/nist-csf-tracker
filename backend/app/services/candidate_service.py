import re
from typing import List, Dict, Any
from sqlmodel import Session, select
from app.models import Control, ArtifactChunk, Evidence


class CandidateService:
    """Service for finding evidence candidates using rules-based matching."""
    
    # Common CSF-related keywords by function
    FUNCTION_KEYWORDS = {
        "Identify": [
            "asset", "inventory", "risk assessment", "vulnerability", "impact",
            "business environment", "governance", "supply chain"
        ],
        "Protect": [
            "access control", "awareness", "training", "data security",
            "maintenance", "protective technology", "encryption", "authentication"
        ],
        "Detect": [
            "anomalies", "continuous monitoring", "detection process",
            "logging", "alerts", "security event", "intrusion detection"
        ],
        "Respond": [
            "response planning", "communications", "analysis", "mitigation",
            "incident response", "improvements", "forensics"
        ],
        "Recover": [
            "recovery planning", "improvements", "communications",
            "business continuity", "disaster recovery", "restoration"
        ]
    }
    
    def __init__(self, session: Session):
        self.session = session
    
    def find_candidates(self, control: Control, limit: int = 20) -> List[Dict[str, Any]]:
        """Find evidence candidates for a given control."""
        # Get all chunks
        statement = select(ArtifactChunk)
        all_chunks = self.session.exec(statement).all()
        
        # Score each chunk
        scored_chunks = []
        for chunk in all_chunks:
            score = self._score_chunk(control, chunk)
            if score > 0:
                scored_chunks.append({
                    "chunk": chunk,
                    "score": score,
                    "match_reasons": self._get_match_reasons(control, chunk)
                })
        
        # Sort by score and return top N
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # Check if already evidence
        existing_evidence_ids = self._get_existing_evidence_chunks(control.id)
        
        # Format results
        candidates = []
        for item in scored_chunks[:limit]:
            chunk = item["chunk"]
            is_existing = chunk.id in existing_evidence_ids
            
            candidates.append({
                "chunk_id": chunk.id,
                "artifact_id": chunk.artifact_id,
                "snippet_text": chunk.chunk_text[:500] + "..." if len(chunk.chunk_text) > 500 else chunk.chunk_text,
                "full_text": chunk.chunk_text,
                "locator": chunk.locator_json,
                "score": item["score"],
                "match_reasons": item["match_reasons"],
                "is_existing_evidence": is_existing
            })
        
        return candidates
    
    def _score_chunk(self, control: Control, chunk: ArtifactChunk) -> float:
        """Score a chunk's relevance to a control."""
        score = 0.0
        text_lower = chunk.chunk_text.lower()
        
        # Score 1: Control ID match (very strong signal)
        if control.csf_id.lower() in text_lower:
            score += 50.0
        
        # Score 2: Control name keywords
        control_name_words = set(control.name.lower().split())
        chunk_words = set(text_lower.split())
        name_overlap = len(control_name_words & chunk_words)
        score += name_overlap * 5.0
        
        # Score 3: Custom keywords if defined
        if control.keywords:
            keywords = [k.strip().lower() for k in control.keywords.split(',')]
            for keyword in keywords:
                if keyword in text_lower:
                    score += 10.0
        
        # Score 4: Function-specific keywords
        function_keywords = self.FUNCTION_KEYWORDS.get(control.function, [])
        for keyword in function_keywords:
            if keyword.lower() in text_lower:
                score += 3.0
        
        # Score 5: Category-specific patterns
        category_score = self._score_category_patterns(control.category, text_lower)
        score += category_score
        
        # Score 6: Locator bonus (e.g., if in a relevant section)
        locator_score = self._score_locator(control, chunk.locator_json)
        score += locator_score
        
        return score
    
    def _score_category_patterns(self, category: str, text: str) -> float:
        """Score based on category-specific patterns."""
        score = 0.0
        
        # Asset Management (ID.AM)
        if category.startswith("ID.AM"):
            patterns = [
                r"asset\s+(?:inventory|register|database|list)",
                r"(?:hardware|software|data)\s+(?:inventory|catalog)",
                r"configuration\s+management\s+database"
            ]
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 8.0
        
        # Access Control (PR.AC)
        elif category.startswith("PR.AC"):
            patterns = [
                r"(?:access|authentication|authorization)\s+(?:control|policy|management)",
                r"(?:role-based|least\s+privilege|need\s+to\s+know)",
                r"(?:multi-factor|two-factor|2FA|MFA)"
            ]
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 8.0
        
        # Security Monitoring (DE.CM)
        elif category.startswith("DE.CM"):
            patterns = [
                r"(?:continuous|security)\s+monitoring",
                r"(?:log|event|alert)\s+(?:management|monitoring|collection)",
                r"(?:SIEM|security\s+information\s+and\s+event)"
            ]
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 8.0
        
        # Incident Response (RS.CO, RS.AN)
        elif category.startswith("RS."):
            patterns = [
                r"incident\s+(?:response|handling|management)",
                r"(?:security\s+incident|breach)\s+(?:procedure|process|plan)",
                r"(?:forensic|root\s+cause)\s+analysis"
            ]
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 8.0
        
        return score
    
    def _score_locator(self, control: Control, locator: dict) -> float:
        """Score based on document location (heading relevance)."""
        score = 0.0
        
        if not locator:
            return score
        
        # Check heading relevance
        heading = None
        if "heading" in locator:
            heading = locator["heading"]
        elif "heading_path" in locator and locator["heading_path"]:
            heading = " ".join(locator["heading_path"])
        
        if heading:
            heading_lower = heading.lower()
            
            # Function-specific headings
            if control.function == "Identify" and any(word in heading_lower for word in ["identify", "assessment", "risk", "asset"]):
                score += 5.0
            elif control.function == "Protect" and any(word in heading_lower for word in ["protect", "security", "access", "control"]):
                score += 5.0
            elif control.function == "Detect" and any(word in heading_lower for word in ["detect", "monitor", "alert", "log"]):
                score += 5.0
            elif control.function == "Respond" and any(word in heading_lower for word in ["respond", "incident", "response"]):
                score += 5.0
            elif control.function == "Recover" and any(word in heading_lower for word in ["recover", "continuity", "disaster", "restoration"]):
                score += 5.0
        
        return score
    
    def _get_match_reasons(self, control: Control, chunk: ArtifactChunk) -> List[str]:
        """Get human-readable match reasons."""
        reasons = []
        text_lower = chunk.chunk_text.lower()
        
        if control.csf_id.lower() in text_lower:
            reasons.append(f"Contains control ID '{control.csf_id}'")
        
        if control.keywords:
            keywords = [k.strip().lower() for k in control.keywords.split(',')]
            matched_keywords = [k for k in keywords if k in text_lower]
            if matched_keywords:
                reasons.append(f"Matches keywords: {', '.join(matched_keywords[:3])}")
        
        function_keywords = self.FUNCTION_KEYWORDS.get(control.function, [])
        matched_func_keywords = [k for k in function_keywords if k.lower() in text_lower]
        if matched_func_keywords:
            reasons.append(f"Contains {control.function} terms: {', '.join(matched_func_keywords[:2])}")
        
        if chunk.locator_json and "heading" in chunk.locator_json:
            reasons.append(f"Found in section: {chunk.locator_json['heading']}")
        
        if not reasons:
            reasons.append("General content match")
        
        return reasons
    
    def _get_existing_evidence_chunks(self, control_id: int) -> set:
        """Get chunk IDs that are already evidence for this control."""
        statement = select(Evidence.chunk_id).where(
            Evidence.control_id == control_id,
            Evidence.status.in_(["pending", "accepted"])
        )
        results = self.session.exec(statement).all()
        return set(results)
