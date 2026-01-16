# NIST CSF 2.0 Evidence Candidate Scoring - Justification

## Scoring Weights

The candidate scoring system uses a rules-based approach to rank document chunks by relevance to NIST CSF 2.0 controls:

### 1. Control ID Match (50 points)
- **Weight**: 50.0
- **Justification**: Direct reference to a NIST CSF control ID (e.g., "GV.OC-01") is the strongest signal that a document explicitly addresses that control.
- **NIST Basis**: NIST CSF 2.0 controls have unique identifiers that organizations should reference in their documentation.

### 2. Control Name Keywords (5 points each)
- **Weight**: 5.0 per matching word
- **Justification**: Words from the control's name appearing in text suggest direct relevance.
- **Example**: For "Organizational Context", matching "organizational" and "context" = 10 points.

### 3. Custom Keywords (10 points each)
- **Weight**: 10.0 per keyword
- **Justification**: Organizations can define domain-specific keywords that indicate control implementation.
- **Use Case**: Custom keywords like "CMDB" for asset management or "SOAR" for incident response.

### 4. Function Keywords (3 points each)
- **Weight**: 3.0 per keyword
- **Justification**: NIST CSF organizes controls by Functions (Govern, Identify, Protect, Detect, Respond, Recover). Terminology associated with each Function indicates general relevance.
- **NIST Basis**: Each Function has characteristic activities and outcomes defined in NIST CSF 2.0 documentation.

### 5. Category-Specific Patterns (8 points each)
- **Weight**: 8.0 per regex pattern match
- **Justification**: Certain control categories have industry-standard terminology:
  - **ID.AM** (Asset Management): "asset inventory", "CMDB", "hardware catalog"
  - **PR.AC** (Access Control): "role-based access", "least privilege", "MFA"
  - **DE.CM** (Security Monitoring): "SIEM", "continuous monitoring", "log management"
  - **RS.** (Respond): "incident response", "forensic analysis", "breach procedure"
- **NIST Basis**: NIST SP 800-53, ISO 27001, and industry frameworks define standard practices for these categories.

### 6. Document Structure (5 points)
- **Weight**: 5.0 for relevant section headings
- **Justification**: Evidence located in appropriately-named document sections (e.g., "Access Control Policy" for PR.AC controls) indicates intentional control coverage.
- **Best Practice**: Well-organized security documentation follows logical structure.

## Total Scoring Range

- **Maximum Possible**: ~150+ points (control ID + multiple keyword matches + patterns)
- **Strong Candidate**: 30+ points
- **Moderate Candidate**: 10-30 points
- **Weak Candidate**: <10 points

## Design Philosophy

**NOT AI-based**: This scoring is deterministic and auditable. Organizations can understand exactly why a document was flagged as relevant.

**Customizable**: Organizations can add custom keywords to improve precision for their environment.

**Conservative**: Higher weights for explicit references (IDs, exact keywords) vs. general terminology.

## Limitations

1. **No Semantic Understanding**: Cannot infer meaning; relies on explicit keyword presence.
2. **Language-Dependent**: Optimized for English; may need localization.
3. **No Context Awareness**: Cannot distinguish between policy stating "we do X" vs. "we don't do X".

## Recommendation

Review candidates with scores >20 first. Lower-scored candidates may still be relevant but require manual judgment.
