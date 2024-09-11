import os, subprocess
from llama_index.core import VectorStoreIndex
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    PropertyGraphIndex,
)

def create_llama_vector_index_rag(llm, embed_model, persist_dir=None, documents=None, vector_store_kwargs={}):
    """
    Create a Llama index from a list of documents.

    Parameters:
    documents (list): A list of documents to index.
    llm (str): The LLM model to use for the index.
    embed_model (str): The embedding model to use for the index.
    persist_dir (str): The directory to save the index to.

    Returns:
    query_engine: The query engine for the Llama index.

    """
    if persist_dir is not None and os.path.exists(persist_dir):
         storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
    else:
         storage_context = None
    if documents is not None:
        vector_index = VectorStoreIndex.from_documents(documents, 
                                                        llm=llm,
                                                        embed_model=embed_model, 
                                                        show_progress=True,
                                                        storage_context=storage_context, 
                                                        **vector_store_kwargs)
    else:
        raise ValueError("Documents must be provided to create the index. Or write a function to fetch the documents you jackleg.")
    
    # save the database
    if persist_dir is not None and not os.path.exists(persist_dir): 
            vector_index.storage_context.persist(persist_dir=persist_dir)
            
    # # convert to query engine
    # query_engine = vector_index.as_query_engine()
    
    return vector_index


def set_neo4j_password(password):
    command = ['neo4j-admin', 'dbms', 'set-initial-password', password]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("Password set successfully.")
        else:
            print(f"Error setting password: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")


def add_lines_to_conf(file_path='/etc/neo4j/neo4j.conf'):
    lines_to_add = [
        "dbms.security.procedures.allowlist=apoc.*\n",
        "dbms.security.procedures.unrestricted=apoc.*\n"
    ]
    
    try:
        with open(file_path, 'a') as file:
            file.writelines(lines_to_add)
        print("Lines added successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_neo4j_graph_store(neo_url="bolt://localhost:7687", password=os.getenv("NEO4J_PWD"), config={"connection_timeout": 240, "connection_acquisition_timeout": 240, "max_connection_pool_size": 1000}):
    graph_store = Neo4jPropertyGraphStore(
        username="neo4j",
        password=password,
        url=neo_url,
        database="neo4j",
        **config
    )
    return graph_store


def neo4j_query(graph_store, query="""MATCH (n) DETACH DELETE n"""):
    return graph_store.structured_query(query)


def create_neo4j_graphrag(documents, llm, embed_model, kg_extractor, graph_store, graph_idx_persist_dir=None, graph_store_persist_dir=None, similarity_top_k=3, graph_kwargs={}):
    if documents is not None and not os.path.exists(graph_idx_persist_dir):
        graph_index = PropertyGraphIndex.from_documents(documents, 
                                                        llm=llm,
                                                        property_graph_store=graph_store, 
                                                        embed_model=embed_model, 
                                                        kg_extractors=[kg_extractor],
                                                        #  transformations=[SentenceSplitter(chunk_size=500, chunk_overlap=50)],
                                                        show_progress=True,
                                                        **graph_kwargs)
    else:
        if os.path.exists(graph_idx_persist_dir):
            graph_index=PropertyGraphIndex.from_existing(property_graph_store=graph_store,
                                 llm=llm,
                                 kg_extractor=[ kg_extractor ], 
                                 embed_model=embed_model,
                                 storage_context=StorageContext.from_defaults(persist_dir=graph_idx_persist_dir),
                                 )
        else:
            raise ValueError("Documents must be provided to create the index. Or write a function to fetch the documents you jackleg.")
    
    if graph_idx_persist_dir is not None: graph_index.storage_context.persist(persist_dir=graph_idx_persist_dir)
    if graph_store_persist_dir is not None: graph_store.persist(persist_path=graph_store_persist_dir)
    query_engine = graph_index.as_query_engine(similarity_top_k=similarity_top_k)
    return query_engine
