starlette-precompressed-static
===

A small library for Starlette, to serve pre-compressed static resources.

## Installation

```
pip install starlette-precompressed-static
```

## Usage

Just replace:

```python
from starlette.staticfiles import StaticFiles

StaticFiles(directory="www")
```

with:

```python
from starlette_precompressed_static import PreCompressedStaticFiles

PreCompressedStaticFiles(directory="www")
```

and you're good to go! By default both brotli and gzip are supported, and brotli is always preferred over gzip.
It is possible to disable one of the algorithms, like so:

```python
PreCompressedStaticFiles(directory="www", gzip=False)
```

## Limitations

This is a very simple implementation, and it has some limitations:

* It wil always try to fetch the compressed version first, and fallback to the uncompressed version if that doesn't exist. This means that if you have some files that should not be compressed (e.g. fonts) they should probably be separated and served by a normal `StaticFiles()`.
* It works by adding `.br` og `.gzip` to the requested path, so it does not support `html` mode were the path may be a folder, or the response a pretty 404.html page.



## A note on older Python versions

This library needs that the Python mimetypes module knows about brotli, which was added in Python 3.9, and therefore only Python 3.9 and newer are supported. It should work fine on older versions as well, but brotli will need to be added to the encodings_map in the mimetypes module, like so:

```python
import mimetypes

if ".br" not in mimetypes.encodings_map:
    # We need brotli to exist in the encodings map, so
    # that brotli encoded files (e.g. xxx.html.br) are
    # detected as the correct file type. This was added
    # in Python 3.9, so on older versions we must add it
    # ourselves.
    mimetypes.encodings_map[".br"] = "br"

```

This may have unexpected side effects, so be aware.
