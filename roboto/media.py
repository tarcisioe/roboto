"""Utility functions for handling InputMedia types."""
import mimetypes
from dataclasses import replace
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Sequence, Tuple, TypeVar, Union
from uuid import uuid4

from .api_types import FileDescription, InputMedia

ConstrainedInputMedia = TypeVar('ConstrainedInputMedia', bound=InputMedia)


def get_mimetype(input_file: Union[Path, BinaryIO]):
    """Fetch the mimetype of an input_file that does not have it explicitly specified.
    """
    if not hasattr(input_file, 'name'):
        return 'application/octet-stream'

    mime_type, _ = mimetypes.guess_type(input_file.name)  # type: ignore

    if mime_type is None:
        return 'application/octet-stream'

    return mime_type


def extract_media(
    media: ConstrainedInputMedia,
) -> Tuple[ConstrainedInputMedia, Optional[FileDescription]]:
    """Extract the InputFile and an attachment version of an InputMedia, if needed."""
    input_file = media.media

    if isinstance(input_file, str):
        return media, None

    attach_name = f'attached{uuid4()}'
    new_media = replace(media, media=f'attach://{attach_name}')

    if isinstance(input_file, FileDescription):
        return (
            new_media,
            replace(input_file, basename=attach_name),
        )

    return (
        new_media,
        FileDescription(
            input_file, mime_type=get_mimetype(input_file), basename=attach_name,
        ),
    )


def extract_medias(
    media: Sequence[ConstrainedInputMedia],
) -> Tuple[List[ConstrainedInputMedia], Dict[str, FileDescription]]:
    """Apply extract_media to a sequence of InputMedia and transpose the result."""
    medias_and_files = [extract_media(m) for m in media]

    medias, files = zip(*medias_and_files)

    return list(medias), {f.basename: f for f in files if f is not None}
