import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _dividir_por_tokens(tokens: list[int], tamano_tokens: int, overlap_tokens: int) -> list[str]:
    paso = max(tamano_tokens - overlap_tokens, 1)
    fragmentos = []
    inicio = 0
    while inicio < len(tokens):
        fin = inicio + tamano_tokens
        fragmento = _ENCODER.decode(tokens[inicio:fin]).strip()
        if fragmento:
            fragmentos.append(fragmento)
        if fin >= len(tokens):
            break
        inicio += paso
    return fragmentos


def chunkear_texto(texto: str, tamano_tokens: int = 500, overlap_tokens: int = 50) -> list[str]:
    """Un chunk por párrafo (separado por línea en blanco), con `tamano_tokens`
    como tope: los párrafos que lo superan se sub-dividen con solapamiento de
    `overlap_tokens`.

    Se evita empaquetar párrafos pequeños hasta llenar el presupuesto de
    tokens porque eso mezcla unidades de información independientes (p. ej.
    varias filas de una tabla) en un mismo chunk y diluye su embedding.
    """
    parrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]
    if not parrafos:
        return []

    chunks = []
    for parrafo in parrafos:
        tokens = _ENCODER.encode(parrafo)
        if len(tokens) <= tamano_tokens:
            chunks.append(parrafo)
        else:
            chunks.extend(_dividir_por_tokens(tokens, tamano_tokens, overlap_tokens))
    return chunks
