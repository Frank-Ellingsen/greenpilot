"""
04_index_knowledge_base.py
Indexes all PDF documents in Kunnskapsbase/ into ChromaDB and a structured JSON knowledge index.
Enables RAG for Streamlit AI Project Controller Copilot.
"""

import os
import glob
import json
import re

try:
    import fitz  # PyMuPDF
    HAVE_FITZ = True
except ImportError:
    HAVE_FITZ = False

try:
    import pypdf
    HAVE_PYPDF = True
except ImportError:
    HAVE_PYPDF = False

try:
    import chromadb
    HAVE_CHROMADB = True
except ImportError:
    HAVE_CHROMADB = False

def extract_pdf_chunks(pdf_path, chunk_size=800, chunk_overlap=100):
    filename = os.path.basename(pdf_path)
    chunks = []
    
    if HAVE_FITZ:
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if not text or not text.strip():
                    continue
                # Split page text into chunks
                paras = [p.strip() for p in text.split("\n\n") if p.strip()]
                curr_chunk = ""
                for p in paras:
                    if len(curr_chunk) + len(p) < chunk_size:
                        curr_chunk += (" " if curr_chunk else "") + p
                    else:
                        if curr_chunk:
                            chunks.append({
                                "source": filename,
                                "page": page_num + 1,
                                "text": curr_chunk.strip()
                            })
                        curr_chunk = p
                if curr_chunk:
                    chunks.append({
                        "source": filename,
                        "page": page_num + 1,
                        "text": curr_chunk.strip()
                    })
            doc.close()
            return chunks
        except Exception as e:
            print(f"Error reading {filename} with fitz: {e}")

    if HAVE_PYPDF:
        try:
            reader = pypdf.PdfReader(pdf_path)
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if not text.strip():
                    continue
                chunks.append({
                    "source": filename,
                    "page": page_num + 1,
                    "text": text.strip()[:1000]
                })
            return chunks
        except Exception as e:
            print(f"Error reading {filename} with pypdf: {e}")

    return chunks

def build_index():
    pdf_files = glob.glob("Kunnskapsbase/*.pdf")
    print(f"Found {len(pdf_files)} PDF files in Kunnskapsbase/.")
    
    all_chunks = []
    chunk_id = 0
    
    for f in pdf_files:
        filename = os.path.basename(f)
        chunks = extract_pdf_chunks(f)
        for c in chunks:
            c["id"] = f"doc_{chunk_id}"
            chunk_id += 1
            all_chunks.append(c)
        print(f"  Indexed {filename}: {len(chunks)} chunks.")

    print(f"Total chunks extracted: {len(all_chunks)}")
    
    # Save to JSON cache for fast keyword / regex fallback
    os.makedirs("data/staging", exist_ok=True)
    cache_path = "data/staging/knowledge_base_chunks.json"
    with open(cache_path, "w", encoding="utf-8") as out:
        json.dump(all_chunks, out, ensure_ascii=False, indent=2)
    print(f"Saved local chunk index to {cache_path}")

    # Build ChromaDB collection
    if HAVE_CHROMADB and all_chunks:
        try:
            chroma_dir = "data/chroma_db"
            os.makedirs(chroma_dir, exist_ok=True)
            client = chromadb.PersistentClient(path=chroma_dir)
            collection = client.get_or_create_collection(name="greenpilot_knowledge")
            
            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]
                ids = [b["id"] for b in batch]
                docs = [b["text"] for b in batch]
                metas = [{"source": b["source"], "page": b["page"]} for b in batch]
                collection.upsert(ids=ids, documents=docs, metadatas=metas)
            print(f"Successfully populated ChromaDB collection 'greenpilot_knowledge' at {chroma_dir}")
        except Exception as e:
            print(f"Note: ChromaDB population skipped or hit warning: {e}")

if __name__ == "__main__":
    build_index()
