# Generation mandate — marketplace domain

You are generating conflict content for a dispute simulation. Two personas are arguing publicly, each convinced they are right. Use whatever language is natural to them — no restrictions, no prescribed words, no outcome in mind.

Personas:
1. "customer" — paid full price for goods that arrived visibly damaged; believes the seller owes a full refund plus compensation; angry, escalating.
2. "vendor" — insists the goods left the warehouse verified and intact; believes any damage happened after delivery; wants the accusation withdrawn and the shop's name cleared.

Write in each persona's own voice, as they would actually type in a public dispute channel.

Output STRICTLY a JSON object, no prose around it:
{"customer": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}, "vendor": {"claims": [4 one-sentence demands/positions/accusations], "noise": [3 short hostile lines that add no substance]}}

Return ONLY the JSON.
