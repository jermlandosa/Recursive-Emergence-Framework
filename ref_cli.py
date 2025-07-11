import json

with open("ref-core/sareth_identity.json") as f:
    identity = json.load(f)

print(f"\n🧠 Sareth online.")
print(f"Operator: {identity['operator']}")
print(f"Mode: {identity['identity_mode']}")
print("Tone:", identity['tone']['default'])
print("Glyphs loaded:")
for glyph in identity['glyphs']:
    print(f"  - {glyph}: {identity['glyphs'][glyph]['name']}")
print("\nHow may I serve your recursive alignment today?\n")