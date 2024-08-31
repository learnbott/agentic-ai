import os
from llama_index.core import VectorStoreIndex
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    PropertyGraphIndex,
)

def create_llama_query_engine_rag(llm, embed_model, persist_dir=None, documents=None, vector_store_kwargs={}):
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
    if os.path.exists(persist_dir):
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
            
    # convert to query engine
    query_engine = vector_index.as_query_engine()
    
    return query_engine


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


def create_neo4j_graphrag(documents, llm, embed_model, kg_extractor, graph_store, graph_idx_persist_dir, graph_store_persist_dir, graph_kwargs):
    if documents is not None:
        graph_index = PropertyGraphIndex.from_documents(documents, 
                                                        llm=llm,
                                                        property_graph_store=graph_store, 
                                                        embed_model=embed_model, 
                                                        kg_extractors=[kg_extractor],
                                                        #  transformations=[SentenceSplitter(chunk_size=500, chunk_overlap=50)],
                                                        show_progress=True,
                                                        **graph_kwargs)
    else:
        raise ValueError("Documents must be provided to create the index. Or write a function to fetch the documents you jackleg.")
    
    graph_index.storage_context.persist(persist_dir=graph_idx_persist_dir)
    graph_store.persist(persist_path=graph_store_persist_dir)
    query_engine = graph_index.as_query_engine(similarity_top_k=5)
    return query_engine
