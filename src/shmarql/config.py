import os, sqlite3, random
import pyoxigraph as px

DEBUG = os.environ.get("DEBUG", "0") == "1"
ENDPOINT = os.environ.get("ENDPOINT")

# SHMARQL_ENDPOINTS variable with name|url pairs
ens = os.environ.get("ENDPOINTS", "")

# Split the string into name|url pairs and then further split each pair
ens_pairs = [pair.split("|") for pair in ens.split(" ") if "|" in pair]

# Convert into a dictionary
ENDPOINTS = {name: url for name, url in ens_pairs}

SCHEME = os.environ.get("SCHEME", "http://")
DOMAIN = os.environ.get("DOMAIN", "127.0.0.1")
PORT = os.environ.get("PORT", "5001")

QUERIES_DB = os.environ.get("QUERIES_DB", "queries.db")
thequerydb = sqlite3.connect(QUERIES_DB)
thequerydb.executescript(
    """CREATE TABLE IF NOT EXISTS queries (queryhash TEXT, query TEXT, timestamp TEXT, endpoint TEXT, result TEXT, duration FLOAT);
pragma journal_mode=WAL;"""
)

FTS_FILEPATH = os.environ.get("FTS_FILEPATH")
RDF2VEC_FILEPATH = os.environ.get("RDF2VEC_FILEPATH")

try:
    CONFIG_STORE = px.Store(os.environ.get("CONFIG_STORE", "config.oxi"))
except:
    CONFIG_STORE = px.Store()

SITE_ID = os.environ.get(
    "SITE_ID", "".join([random.choice("abcdef0123456789") for _ in range(10)])
)


prefixes = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX virtrdfdata: <http://www.openlinksw.com/virtrdf-data-formats#>
PREFIX virtrdf: <http://www.openlinksw.com/schemas/virtrdf#>
PREFIX shmarql: <https://shmarql.com/>
PREFIX cto: <https://nfdi4culture.de/ontology#>
PREFIX nfdi4culture: <https://nfdi4culture.de/id/>
PREFIX nfdicore: <https://nfdi.fiz-karlsruhe.de/ontology/>
PREFIX factgrid: <https://database.factgrid.de/entity/>
"""

CONFIG_STORE.add(
    px.Quad(
        px.NamedNode(f"https://shmarql.com/site/{SITE_ID}"),
        px.NamedNode("https://shmarql.com/settings/prefixes"),
        px.Literal(prefixes),
        None,
    )
)


def get_setting(key: str, default=""):
    for s, p, o, _ in CONFIG_STORE.quads_for_pattern(
        px.NamedNode(f"https://shmarql.com/site/{SITE_ID}"),
        px.NamedNode(f"https://shmarql.com/settings/{key}"),
        None,
    ):
        return o.value
    return default