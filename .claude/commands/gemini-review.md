---
description: Analyze Gemini code review recommendations for a PR and provide disposition advice
---

You are analyzing Gemini Code Assist recommendations for a GitHub PR. Follow this workflow:

## Step 1: Fetch and Present Recommendations

Run the analysis script to fetch Gemini's review comments:

```bash
python scripts/analyze_gemini_recommendations.py {{arg1}}
```

This will:

- Fetch all Gemini bot comments from the PR
- Extract severity levels (HIGH, MEDIUM, LOW)
- Present them in a structured format for your analysis

## Step 2: Analyze Each Recommendation

For EACH recommendation presented, provide:

### Your Evaluation:

- **Technical Validity:** Is the recommendation technically correct?
- **Relevance:** Does it align with current phase goals?
- **Architecture Alignment:** Does it fit our design decisions?
- **Already Implemented Check:** Search commits and code to verify if already fixed

### Disposition Recommendation:

Choose ONE:

- **ALREADY_IMPLEMENTED** - Feature/fix already exists (check recent commits first!)
- **IMPLEMENT** - Valid, should be implemented now or soon
- **DEFER** - Valid, but defer to future phase
- **REJECT** - YAGNI, over-engineering, or conflicts with design

### Rationale:

One sentence explaining your recommendation

### Scope (if IMPLEMENT):

Brief description of implementation work needed

## Step 3: Create Decision Record

After providing your analysis for all recommendations:

1. Create a JSON file with structured decisions:

```json
{
  "pr_number": {{arg1}},
  "decisions": [
    {
      "number": 1,
      "recommendation": "Brief summary...",
      "severity": "HIGH|MEDIUM|LOW",
      "disposition": "ALREADY_IMPLEMENTED|IMPLEMENT|DEFER|REJECT",
      "rationale": "Your one-sentence rationale",
      "scope": "Implementation scope (if IMPLEMENT)",
      "file": "path/to/file.py",
      "line": 123,
      "commit": "abc1234 (if already implemented)"
    }
  ]
}
```

2. Save to `.user/gemini-decisions/pr{{arg1}}-decisions.json`

3. Run the decision recorder:

```bash
python scripts/record_gemini_decisions.py {{arg1}} .user/gemini-decisions/pr{{arg1}}-decisions.json
```

## Step 4: Implement if Needed

For any IMPLEMENT recommendations:

- If small fixes, implement immediately in the same session
- If larger work, create tracking issues or follow-up PRs
- Update the decision record when completed

## Important Checks

Before dispositioning as ALREADY_IMPLEMENTED:

1. **Check recent commits** - especially in the PR's branch
2. **Search codebase** - verify the fix actually exists
3. **Read relevant files** - confirm implementation matches recommendation
4. **Cite commit hash** - include in rationale for traceability

## Output Format

Present your analysis in a clean, structured format:

```
## Gemini Review Analysis: PR #{{arg1}}

### Recommendation 1: [SEVERITY] Brief Title

**Gemini's Feedback:**
[Quote the recommendation]

**My Evaluation:**
Technically valid and [critical/important/nice-to-have]
[Detailed analysis]

**Disposition:** ALREADY_IMPLEMENTED | IMPLEMENT | DEFER | REJECT

**Rationale:** [One sentence]

**Evidence/Scope:** [Commit hash if implemented, or scope if implementing]

---

[Repeat for all recommendations]

## Summary

- Total Recommendations: X
- ALREADY_IMPLEMENTED: X
- IMPLEMENT: X
- DEFER: X
- REJECT: X

[If any IMPLEMENT items, list next steps]
```

## Notes

- This is collaborative - discuss any unclear recommendations with the user
- Prioritize HIGH severity items
- Be thorough in checking if already implemented
- Document rationale clearly for future reference
