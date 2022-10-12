import os
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import CancelledError

from PIL import Image
from gi.repository import GLib
from gi.repository import GdkPixbuf

from . import helpers
from .data_helpers import find_data_path


THUMBNAIL_BROKEN = GdkPixbuf.Pixbuf.new_from_file(
    find_data_path("images/thumbnail_broken.svg")
)


def preview_gdk_pixbuf_from_image(image_path, size=64):
    """Generates a thumbnail for the image at the given path and returns it as
    a Gdk Pixbuf.

    :param str image_path: the path of the image.
    :param int size: The size of the preview (optional, default: ``64``).

    :rtype: GdkPixbuf.Pixbuff
    """
    EXIF_TAG_ORIENTATION = 274
    ORIENTATION_OPERATIONS = {
        1: [],
        2: [Image.FLIP_LEFT_RIGHT],
        3: [Image.ROTATE_180],
        4: [Image.FLIP_TOP_BOTTOM],
        5: [Image.FLIP_LEFT_RIGHT, Image.ROTATE_90],
        6: [Image.ROTATE_270],
        7: [Image.FLIP_LEFT_RIGHT, Image.ROTATE_270],
        8: [Image.ROTATE_90],
    }

    image = None
    image_rgba = None

    try:
        image = helpers.open_image_from_path(image_path)
    except Exception as error:
        print(
            "E: An error occured when thumbnailing '%s': %s"
            % (image_path, str(error))
        )
    else:
        image_rgba = Image.new("RGBA", image.size)
        image_rgba.paste(image)
        image_rgba.thumbnail([size, size], Image.BOX, reducing_gap=1.0)

        # Handle JPEG orientation
        if image.format == "JPEG":
            exif = image.getexif()
            if (
                EXIF_TAG_ORIENTATION in exif
                and exif[EXIF_TAG_ORIENTATION] in ORIENTATION_OPERATIONS
            ):
                orientation = exif[EXIF_TAG_ORIENTATION]
                for operation in ORIENTATION_OPERATIONS[orientation]:
                    image_rgba = image_rgba.transpose(operation)

        # fmt: off
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(
            GLib.Bytes.new(image_rgba.tobytes()),  # data
            GdkPixbuf.Colorspace.RGB,              # colorspace
            True,                                  # has alpha
            8,                                     # bits_per_sample
            *image_rgba.size,                      # width, height
            image_rgba.size[0] * 4,                # rowstride
        )
        # fmt: on

    finally:
        if image:
            image.close()
        if image_rgba:
            image_rgba.close()

    return pixbuf


def preview_gdk_pixbuf_from_thumbnail(thumbnail_path, size=64):
    """Loads the given thumbnail and returns it as a Gdk Pixbuf.

    :param str thumbnail_path: the path of the image.
    :param int size: The size of the preview (optional, default: ``64``).

    :rtype: GdkPixbuf.Pixbuff
    """
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
        thumbnail_path, size, size, True
    )
    return pixbuf


def get_cached_thumbnail_path(file_path):
    """Find the smallest thumbnail available in the cache for the file at the
    given path.

    :param str file_path: The original file path.

    :rtype: str or None
    :return: The path of the thumbnail if it exists in the cache, else returns
             ``None``.
    """
    _THULBNAIL_SIZE = ["normal", "large", "x-large", "xx-large"]

    for thumbnail_path in (
        helpers.get_thumbnail_path_for_file(file_path, size)
        for size in _THULBNAIL_SIZE
    ):
        if os.path.isfile(thumbnail_path):
            return thumbnail_path

    return None


class Thumbnailer:
    _MAX_WORKERS = 2

    def __init__(self):
        # {<uuid>: {"future": future, "iter": iter_, "callback": fn(iter_, pixbuf)}}
        self._pending = {}
        self._executor = ThreadPoolExecutor(max_workers=self._MAX_WORKERS)

    def generate(self, uuid, iter_, image_path, callback):
        # This thumbnail has already been submitted
        if uuid in self._pending:
            return

        def _thumbnail_callback(future):
            # The thumbnail has been canceled so we should not go further
            if uuid not in self._pending:
                return

            try:
                pixbuf = future.result()
            except OSError as error:
                print(
                    "E: An error occured when generating thumbnail for '%s': %s"
                    % (image_path, str(error))
                )
                pixbuf = THUMBNAIL_BROKEN
            except CancelledError:
                return
            self._pending[uuid]["callback"](iter_, pixbuf)
            del self._pending[uuid]

        cached_thumbnail_path = get_cached_thumbnail_path(image_path)
        if cached_thumbnail_path:
            future = self._executor.submit(
                preview_gdk_pixbuf_from_thumbnail, cached_thumbnail_path
            )
        else:
            future = self._executor.submit(
                preview_gdk_pixbuf_from_image, image_path
            )
        future.add_done_callback(_thumbnail_callback)

        self._pending[uuid] = {
            "future": future,
            "iter": iter_,
            "callback": callback,
        }

    def cancel(self, uuid):
        if uuid not in self._pending:
            return
        self._pending[uuid]["future"].cancel()
        del self._pending[uuid]

    def cancel_all(self):
        self._pending = {}
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._executor = ThreadPoolExecutor(max_workers=self._MAX_WORKERS)
