# Generation mandate — debt domain

You are generating conflict content for a dispute simulation. Two personas are arguing publicly, each convinced they are right. Use whatever language is natural to them — no restrictions, no prescribed words, no outcome in mind.

Personas:
1. "lender" — lent a substantial sum to someone they trusted; the repayment deadline passed months ago; insists on the full principal plus the agreed interest, now.
2. "borrower" — believes the claimed principal is overstated and that proper statements were never provided; feels pressured and wants a repayment plan they can actually meet.

Write in each persona's own voice, as they would actually type in a public dispute channel.

Output STRICTLY a JSON object, no prose around it:
{"lender": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}, "borrower": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}}

Return ONLY the JSON.
