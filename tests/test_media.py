"""Tests for the roboto.media module."""
from io import BytesIO
from pathlib import Path
from typing import List, Union

from roboto import URL, FileDescription, FileID, InputMediaPhoto, InputMediaVideo
from roboto.media import extract_media, extract_medias, get_mimetype


def test_get_mimetype() -> None:
    """Ensure get_mimetype gets mimetypes correctly."""
    assert get_mimetype(Path('test.jpg')) == 'image/jpeg'
    assert get_mimetype(Path('test')) == 'application/octet-stream'
    assert get_mimetype(BytesIO(b'data')) == 'application/octet-stream'


def test_extract_media_does_not_affect_url() -> None:
    """Ensure extract_media does nothing if the media is just a URL."""
    input_media = InputMediaPhoto(URL.make('https://example.com/bla.jpg'))

    media, input_file = extract_media(input_media)

    assert media is input_media
    assert input_file is None


def test_extract_media_does_not_affect_fileid() -> None:
    """Ensure extract_media does nothing if the media is just a FileID."""
    input_media = InputMediaPhoto(FileID('AAAAAAAAAAA'))

    media, input_file = extract_media(input_media)

    assert media is input_media
    assert input_file is None


def test_extract_media_extracts_file() -> None:
    """Ensure extract_media extracts a FileDescription and sets attachment correctly."""
    extracted_media, extracted_file = extract_media(InputMediaPhoto(Path('test.jpg')))

    assert isinstance(extracted_media.media, str)
    assert extracted_media.media.startswith('attach://')
    assert extracted_file is not None
    assert extracted_media.media.replace('attach://', '') == extracted_file.basename


def test_extract_media_keeps_custom_mimetype() -> None:
    """Ensure extract_media keeps the custom mimetype of a FileDescription."""
    extracted_media, extracted_file = extract_media(
        InputMediaPhoto(
            FileDescription(Path('test'), mime_type='image/jpeg', basename='image.jpg')
        )
    )

    assert isinstance(extracted_media.media, str)
    assert extracted_media.media.startswith('attach://')
    assert extracted_file is not None
    assert extracted_media.media.replace('attach://', '') == extracted_file.basename
    assert extracted_file.mime_type == 'image/jpeg'


def test_extract_medias() -> None:
    """Ensure extract_medias extract the correct medias and sets the correct
    attachments.
    """
    medias: List[Union[InputMediaPhoto, InputMediaVideo]]

    medias, files = extract_medias(
        [
            InputMediaPhoto(URL.make('https://example.com/bla.jpg')),
            InputMediaVideo(FileID('AAAAAAAAAAA')),
            InputMediaPhoto(Path('test.jpg')),
            InputMediaVideo(
                FileDescription(
                    Path('test'), mime_type='video/mp4', basename='image.jpg'
                )
            ),
        ]
    )

    assert isinstance(medias[2].media, str)
    assert medias[2].media.startswith('attach://')
    assert isinstance(medias[3].media, str)
    assert medias[3].media.startswith('attach://')

    assert len(files) == 2

    attach_name_0 = medias[2].media.replace('attach://', '')
    attach_name_1 = medias[3].media.replace('attach://', '')

    assert attach_name_0 in files
    assert attach_name_1 in files

    assert files[attach_name_0].basename == attach_name_0
    assert files[attach_name_1].basename == attach_name_1
