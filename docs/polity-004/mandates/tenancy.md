# Generation mandate — tenancy domain

You are generating conflict content for a dispute simulation. Two personas are arguing publicly, each convinced they are right. Use whatever language is natural to them — no restrictions, no prescribed words, no outcome in mind.

Personas:
1. "landlord" — says the tenant left the unit damaged and owing back rent; is withholding the deposit and billing for repairs and lost rent.
2. "tenant" — says they reported serious maintenance problems that were ignored for months and wants the deposit back plus a rent abatement.

Write in each persona's own voice, as they would actually type in a public dispute channel.

Output STRICTLY a JSON object, no prose around it:
{"landlord": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}, "tenant": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}}

Return ONLY the JSON.
