def chunk_text(text:str, chunk_size:int=1200, overlap:int=200):
    chunks=[] 
    start=0
    while start < len(text):
        end=min(start+chunk_size,len(text))
        chunks.append(text[start:end])
        start=max(end-overlap,end)
    return chunks
