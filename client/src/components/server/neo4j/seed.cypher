CREATE (u:User {id: $userId, name: $name})
CREATE (t:Theme {name: $theme})
CREATE (r:Reflection {text: $reflection})
CREATE (tc:TruthCore {summary: $truthCore})

MERGE (u)-[:SHARED]->(r)
MERGE (r)-[:RELATES_TO]->(t)
MERGE (t)-[:COMPRESSED_INTO]->(tc)
