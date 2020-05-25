import mimetypes

from typing import BinaryIO, NamedTuple, Optional
from pathlib import Path

from anyio import aopen


class PathMultipartData(NamedTuple):
    '''
    Describes a file to be sent in a multipart/form-data request with a Path.

    This should be used for sending a file by its Path with (optional)
    manually-specified mimetype and basename.
    '''
    path: Path
    mime_type: str = 'application/octet-stream'
    basename: Optional[str] = None


class BytesMultipartData(NamedTuple):
    '''
    Describes a file to be sent in a multipart/form-data request with raw bytes.

    This should be used for sending raw bytes with (optional)
    manually-specified mimetype and basename.
    '''
    binary_data: bytes
    mime_type: str = 'application/octet-stream'
    basename: Optional[str] = None


class IOMultipartData(NamedTuple):
    '''
    Describes a file to be sent in a multipart/form-data request with BinaryIO.

    This should be used for manually specifying the mimetype or the basename of
    a file to be sent, or to send data from an in-memory file-like object.
    '''
    binary_data: BinaryIO
    mime_type: str = 'application/octet-stream'
    basename: Optional[str] = None


async def _file_like_to_multipart_data(value):
    if isinstance(value, Path):
        async with await aopen(value, 'rb') as f:
            file_bytes = await f.read()

        mime_type, _ = mimetypes.guess_type(value)

        file_basename = value.name

        return file_bytes, mime_type, file_basename

    if hasattr(value, 'read'):
        file_bytes = value.read()

        if not isinstance(value.name, str):
            return file_bytes, None, None

        file_basename = Path(value.name).name if hasattr(value, 'name') and isinstance(value.name, str) else None

        mime_type, _ = mimetypes.guess_type(file_basename) if file_basename is not None else (None, None)

        return file_bytes, mime_type, file_basename

    if isinstance(value, PathMultipartData):
        path, mime_type, file_basename = value

        async with await aopen(path, 'rb') as f:
            file_bytes = await f.read()

        return file_bytes, mime_type, file_basename

    if isinstance(value, BytesMultipartData):
        return value

    if isinstance(value, IOMultipartData):
        bytes_io, mime_type, file_basename = value

        file_bytes = bytes_io.read()

        return file_bytes, mime_type, file_basename

    raise TypeError('value should be of type Path, PathMultipartData, '
                    'BytesMultipartData, IOMultipartData, or provide a `read` method.')


async def _to_multipart_form_data(value, encoding):
    if isinstance(value, (Path, BytesMultipartData, IOMultipartData)) or hasattr(value, 'read'):
        file_bytes, mime_type, file_basename = await _file_like_to_multipart_data(value)

        mime_type = 'application/octet-stream' if mime_type is None else mime_type

        return file_bytes, mime_type, file_basename

    return str(value).encode(encoding), None, None


async def multipart_blocks(values, encoding, boundary_data):
    '''
    Build a multipart request body out of a values dictionary from a request.
    '''
    boundary = b''.join((b'--', bytes(boundary_data, encoding)))

    for k, v in values.items():
        field_bytes, mime_type, filename = await _to_multipart_form_data(v, encoding)

        yield b''.join(
            b
            for b in (
                boundary,
                b'\r\n',
                f'Content-Disposition: form-data; name="{k}"'.encode(encoding),
                (
                    None
                    if filename is None
                    else f'; filename="{filename}"'.encode(encoding)
                ),
                (
                    None
                    if mime_type is None
                    else f'; Content-Type: {mime_type}'.encode(encoding)
                ),
                b'\r\n\r\n',
                field_bytes,
                b'\r\n',
            )
            if b is not None
        )

    yield boundary + b'--\r\n'
