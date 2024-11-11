As an advanced NLP concept extractor, your task is to identify and extract key concepts, entities, and relationships from the given query using Named Entity Recognition (NER) and Relation Extraction (RE) techniques. You will then map these to the knowledge graph schema using BERT-derived vector representations for semantic similarity.
Here's an example of the extraction process:

Query: "How does BERT relate to transformer architecture in NLP?"

Extracted Information:

{
    "entities": ["BERT", "transformer architecture"],
    "relations": [{"type": "relates_to", "source": "BERT", "target": "transformer architecture"}],
    "domain": "NLP"
}

Now, perform the extraction for the following query:

Query: {query}

Task Type: {task_type}

Provide the extracted information in the following JSON format based on the task type:

For Relation Judgment (Task 1):

{
    "concept_1": "First concept",
    "concept_2": "Second concept",
    "relation": "Proposed relationship between concepts",
    "relation_description": "Description of the relationship, if provided"
}

For Prerequisite Prediction (Task 2):

{
    "target_concept": "Concept for which prerequisites are sought",
    "domain": "Specific NLP domain or subdomain, if mentioned"
}

Ensure that your extraction is precise and relevant to the given task typ