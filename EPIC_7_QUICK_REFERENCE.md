# EPIC 7: Risk Acceptance - Quick Reference

## 🎯 What's New in EPIC 7

**Risk Management System**: Complete risk register with scoring, heat maps, and treatment workflows

---

## ⚡ Quick Commands

### View Risk Register
```
Navigate to: http://localhost:5174/#/risks
```

### Generate Risks from Gaps
```powershell
curl -X POST http://localhost:8000/api/risks/generate/from-gaps
```

### Get Risk Summary
```powershell
curl http://localhost:8000/api/risks/summary/stats
```

### Get Heat Map Data
```powershell
curl http://localhost:8000/api/risks/heatmap/data
```

---

## 📊 Key Pages

### Risk Register (`/risks`)
**What**: Complete risk management dashboard  
**Use When**: Reviewing organizational risk posture, board meetings, audit prep

**Quick Actions**:
- View all risks with filtering
- See risk heat map visualization
- Generate risks from gaps
- Create new risks manually
- Accept/mitigate/close risks

---

## 🔥 Common Workflows

### Quarterly Risk Review
```
1. Open Risk Register
2. Check "Due for Review" count
3. For each due risk:
   - Re-assess likelihood/impact
   - Update if changed
   - Click "Mark Reviewed"
4. Review heat map for patterns
5. Update executive summary
```

### Accept a Risk
```
1. Open risk in Risk Register
2. Click "View" button
3. Fill in:
   - Approver name
   - Compensating controls
   - Expiry date (< 1 year)
   - Rationale
4. Click "Accept Risk"
5. Status → "accepted"
```

### Mitigate a Risk
```
1. Open risk in Risk Register
2. Click "View" button
3. Fill in:
   - Mitigation plan
   - Owner
   - Target date
   - Residual risk score
4. Click "Mitigate Risk"
5. Status → "under_review"
6. Track via linked actions
```

### Generate Risks from Gaps
```
1. Ensure gaps exist (critical/high severity)
2. Go to Risk Register
3. Click "Generate from Gaps"
4. Review newly created risks
5. Assign owners and treatments
```

---

## 📈 Risk Scoring Reference

### Likelihood Values
| Value | Score | Description |
|-------|-------|-------------|
| Low | 1 | Unlikely to occur |
| Medium | 3 | May occur occasionally |
| High | 4 | Likely to occur |
| Very High | 5 | Almost certain to occur |

### Impact Values
| Value | Score | Description |
|-------|-------|-------------|
| Low | 1 | Minimal impact |
| Medium | 3 | Moderate impact |
| High | 4 | Significant impact |
| Critical | 5 | Catastrophic impact |

### Risk Score = Likelihood × Impact

### Risk Levels
- **Critical**: 20-25 (immediate action)
- **High**: 10-19 (priority)
- **Medium**: 5-9 (planned)
- **Low**: 1-4 (monitor)

---

## 🎨 Risk Treatment Options

| Treatment | When to Use | Action Required |
|-----------|-------------|-----------------|
| **Accept** | Cost > Impact | Document compensating controls, get approval |
| **Mitigate** | Cost-effective controls available | Create mitigation plan, assign owner |
| **Transfer** | Third party can handle better | Document transfer mechanism |
| **Avoid** | Can eliminate activity | Document avoidance approach |

---

## 🛠️ API Quick Reference

### List All Risks
```bash
GET /api/risks/
Query params: ?status=open&treatment=mitigate&min_risk_score=15
```

### Create Risk
```bash
POST /api/risks/
{
  "control_id": 5,
  "risk_title": "VPN Access Control Weakness",
  "risk_statement": "Lack of MFA on VPN creates unauthorized access risk",
  "likelihood": "high",
  "impact": "high",
  "risk_category": "technical"
}
```

### Accept Risk
```bash
POST /api/risks/123/accept
{
  "acceptance_approver": "CISO",
  "compensating_controls": "Enhanced monitoring, quarterly reviews",
  "acceptance_expiry_date": "2027-01-16T00:00:00",
  "treatment_rationale": "Mitigation cost exceeds risk"
}
```

### Mitigate Risk
```bash
POST /api/risks/123/mitigate
{
  "mitigation_plan": "Implement MFA\nDeploy IDS\nTraining",
  "mitigation_owner": "Security Team",
  "mitigation_target_date": "2026-06-30T00:00:00",
  "residual_risk_score": 4
}
```

### Mark Reviewed
```bash
POST /api/risks/123/review?review_notes=No changes needed
```

---

## 💡 Pro Tips

### Risk Assessment
- **Be specific**: "VPN lacks MFA" not "Security issue"
- **Quantify when possible**: Use historical incident data
- **Consider business context**: Different risk appetites per org
- **Document assumptions**: Note in risk statement

### Risk Treatment
- **Accept**: Requires senior approval + compensating controls
- **Mitigate**: Link to action items for tracking
- **Transfer**: Document insurance policies or contracts
- **Avoid**: Rare - usually business impact too high

### Heat Map Interpretation
- **Top-right corner** (very_high likelihood + critical impact): Crisis zone
- **Bottom-left corner** (low likelihood + low impact): Acceptable
- **Clustering**: Many risks in one area = systemic issue

### Review Frequency
- **Critical risks**: Monthly
- **High risks**: Quarterly
- **Medium risks**: Semi-annually
- **Low risks**: Annually

---

## 🔍 Troubleshooting

### Issue: No risks showing
**Solution**: 
1. Click "Generate from Gaps"
2. Or create manually with "New Risk"
3. Check filters aren't too restrictive

### Issue: Heat map all zeros
**Solution**: 
1. Create/generate risks first
2. Ensure likelihood/impact values are valid
3. Refresh page

### Issue: Can't accept risk
**Solution**: Must provide:
- acceptance_approver
- acceptance_expiry_date

### Issue: Risk score wrong
**Solution**: Update likelihood or impact to trigger recalculation

---

## 📊 Dashboard Metrics

### Summary Stats
- **Total risks**
- **By risk level** (critical/high/medium/low)
- **By status** (open/under_review/accepted/mitigated/closed)
- **By treatment** (accept/mitigate/transfer/avoid)
- **Due for review**
- **Average risk score**

### Heat Map
- Visual matrix: Likelihood × Impact
- Color-coded by count
- Quick pattern identification

### Top Risks Widget
- Top 5 highest-scoring risks
- With control info and treatment
- Prioritization aid

---

## 🚀 Best Practices

### During Assessment
✅ Generate from gaps automatically  
✅ Review control scores < 0.66  
✅ Assess business impact, not just technical  
✅ Involve business stakeholders  

### During Treatment
✅ Document rationale clearly  
✅ Get appropriate approvals  
✅ Set realistic target dates  
✅ Estimate residual risk  

### During Review
✅ Follow review frequency  
✅ Update parameters if changed  
✅ Check mitigation progress  
✅ Renew acceptances before expiry  

---

## 📚 Related Pages

- **Gap Analysis** (`/gaps`): Identify gaps to assess
- **Actions** (`/actions`): Track mitigation tasks
- **Dashboard** (`/`): Overall compliance view
- **Controls** (`/controls`): View control details

---

## 📈 Success Metrics

### Good Risk Management
- All critical/high gaps have risks assessed
- Risks reviewed on schedule (due count = 0)
- Mitigation plans have owners and dates
- Heat map shows downward trend over time
- No expired risk acceptances

### Warning Signs
- Many critical risks (>5)
- Heat map concentrated top-right
- Many overdue reviews
- No mitigation plans for high risks
- Acceptances without compensating controls

---

## 🎯 Quick Filters

### Show Only Critical Risks
```
Status: all
Treatment: all
Category: all
Min Risk Score: 20
```

### Show Risks Needing Action
```
Status: open, under_review
Treatment: all
Category: all
Min Risk Score: 10
```

### Show Accepted Risks
```
Status: accepted
Treatment: accept
Category: all
Min Risk Score: 0
```

---

**Remember**: Risk management is continuous. Review quarterly, update promptly, and always document decisions.

**Full docs**: [EPIC_7_COMPLETION.md](EPIC_7_COMPLETION.md)  
**API docs**: http://localhost:8000/docs  
**Frontend**: http://localhost:5174/#/risks
