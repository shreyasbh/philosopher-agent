from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.onprem.inmemory import Redis
from diagrams.generic.storage import Storage
from diagrams.generic.network import Firewall

GRAPH_ATTR = {
    "fontsize": "16",
    "pad": "1.2",
    "splines": "ortho",
    "bgcolor": "white",
}
NODE_ATTR = {"fontsize": "13"}

# ── Data Pipeline ──────────────────────────────────────────────────────────────
with Diagram(
    "Philosopher Knowledge Engine — Data Pipeline",
    filename="data_pipeline",
    direction="TB",
    show=False,
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    source = Storage("Video / Audio\nFiles")

    with Cluster("Ingestion & Processing"):
        transcribe = Server("faster-whisper\n(Transcription)")
        translate  = Server("Google Translate\n(Hindi → English)")
        flag       = Server("LLM Flagging\n(GPT-4)\nflags unclear segments only")
        gate1      = Firewall("Quality Gate\nconfidence threshold")
        chunk      = Server("Semantic Chunking\nsliding window + overlap")
        tag        = Server("Metadata Tagging\n(GPT-4)\ntopics · trust · session")
        embed      = Server("Embedding\ntext-embedding-3-small")
        gate2      = Firewall("Quality Gate\nsemantic consistency\nvs AP Framework")

    qdrant = Redis("Qdrant\nVector DB (local)")

    (
        source
        >> transcribe
        >> translate
        >> flag
        >> gate1
        >> chunk
        >> tag
        >> embed
        >> gate2
        >> qdrant
    )

# ── Query Pipeline ─────────────────────────────────────────────────────────────
with Diagram(
    "Philosopher Knowledge Engine — Query Pipeline",
    filename="query_pipeline",
    direction="TB",
    show=False,
    graph_attr=GRAPH_ATTR,
    node_attr=NODE_ATTR,
):
    cli_in = User("User Query\n(CLI)")

    with Cluster("Query Translation Layer\n(user vocab → AP Framework vocab)"):
        translator = Server("Intent Classifier\n+ Vocabulary Mapper")

    with Cluster("Retrieval"):
        orchestrator = Server("Search Orchestrator\nrank: trust · relevance · clarity\nlost-in-middle aware assembly")
        qdrant       = Redis("Qdrant\nVector DB (local)")

    with Cluster("Generation"):
        llm = Server("GPT-4\nAP Framework system prompt\n+ concept glossary")

    cli_out = User("CLI Output")

    cli_in >> translator >> orchestrator
    orchestrator >> Edge(label="semantic search") >> qdrant
    qdrant >> Edge(label="ranked chunks") >> orchestrator
    orchestrator >> Edge(label="assembled context") >> llm
    llm >> cli_out
