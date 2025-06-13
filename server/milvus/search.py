from pymilvus import Collection


def search_in_milvus(collection: Collection, query_embedding, top_k=5):
    """
    Realiza una búsqueda en Milvus utilizando el embedding de la consulta.
    :param collection: Colección de Milvus
    :param query_embedding: Embedding de la consulta
    :param top_k: Número de resultados que se desean recuperar
    :return: Resultados de la búsqueda
    """
    search_params = {
        "metric_type": "L2",  # Métrica L2 para la comparación de vectores
        "params": {"nprobe": 10},  # Parámetros adicionales para la búsqueda
    }

    results = collection.search(
        [query_embedding], "embedding", param=search_params, limit=top_k
    )
    return results
