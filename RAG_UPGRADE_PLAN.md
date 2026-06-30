# RAG Upgrade Plan

## V1.0 Current State

V1.0 uses `KeywordRetriever` as the default retriever. It searches
`knowledge_chunks.content`, `knowledge_chunks.keywords`, and
`knowledge_documents.title`, then returns structured sources with chunk id,
document id, document title, document type, score, and metadata.

The Agent pipeline calls the retriever through `get_retriever()`, so later RAG
upgrades do not need to rewrite Agent nodes.

## V1.1 Target: embedding + pgvector

V1.1 should replace or supplement keyword search with embedding + pgvector:

1. Add document upload for PDF, DOCX, TXT, Markdown, and HTML.
2. Normalize uploaded text and store original document metadata.
3. Split content into chunk records with stable `chunk_index`, source page, and
   section metadata.
4. Generate embedding vectors for each chunk.
5. Store vectors in PostgreSQL using pgvector.
6. Add `VectorRetriever` implementation for semantic search.
7. Add hybrid retrieval that combines keyword recall and vector similarity.
8. Return 引用来源 for every answer, including document title, chunk id, score,
   page or section metadata, and excerpt.
9. Add retrieval evaluation metrics such as hit rate, no-answer rate, and manual
   correction rate.

## Evaluation Metrics

- Hit rate: percentage of answers whose sources include the expected document.
- No-answer rate: percentage of queries where retrieval finds no useful source.
- Manual correction rate: percentage of Agent replies changed by reviewers.
- Source precision: percentage of displayed sources actually used by the reply.
- Fallback rate: percentage of vector retrieval attempts that fall back to
  `KeywordRetriever`.

## Proposed Schema Additions

- `knowledge_documents.source_file_name`
- `knowledge_documents.source_mime_type`
- `knowledge_documents.version`
- `knowledge_chunks.embedding`
- `knowledge_chunks.source_page`
- `knowledge_chunks.source_section`
- `knowledge_chunks.token_count`

## Operational Notes

- Keep `KeywordRetriever` available as fallback.
- Do not block Agent execution if vector retrieval fails; fall back to keyword
  retrieval and record the fallback reason in Agent node logs.
- Run embedding jobs asynchronously for large uploads.
- Avoid storing API keys or embedding provider secrets in the database.
