LOAD CSV WITH HEADERS FROM 'file:///clean_graph_data.csv' AS row
MERGE (t:Track {
    id: row.track_id, 
    name: row.track_name, 
    duration_ms: toInteger(row.duration_ms), 
    explicit: toBoolean(row.explicit), 
    track_number: toInteger(row.track_number)
})
MERGE (a:Artist {
    id: row.artist_id, 
    name: row.artist_name, 
    followers: toInteger(row.followers), 
    popularity: toInteger(row.popularity)
})
MERGE (b:Album {
    id: row.album_id, 
    name: row.album_name, 
    release_date: row.release_date
})
MERGE (a)-[:CREATED]->(t)
MERGE (b)-[:INCLUDES]->(t);

MATCH (a:Artist)-[r:CREATED]->(t:Track)<-[v:INCLUDES]-(b:Album)
RETURN a, t, b
LIMIT 300;

