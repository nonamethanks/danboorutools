from danboorutools.logical.parsers import ParsableUrl, UrlParser
from danboorutools.logical.urls.fantia import FantiaFanclubAssetUrl, FantiaFanclubUrl, FantiaImageUrl, FantiaPostUrl, FantiaUrl


class FantiaJpParser(UrlParser):

    @classmethod
    def match_url(cls, parsable_url: ParsableUrl) -> FantiaUrl | None:
        instance: FantiaUrl
        match parsable_url.url_parts:
            # posts:
            # https://c.fantia.jp/uploads/post/file/1070093/main_16faf0b1-58d8-4aac-9e86-b243063eaaf1.jpeg (sample)
            # https://c.fantia.jp/uploads/post/file/1070093/16faf0b1-58d8-4aac-9e86-b243063eaaf1.jpeg
            # https://cc.fantia.jp/uploads/post_content_photo/file/4563389/main_a9763427-3ccd-4e51-bcde-ff5e1ce0aa56.jpg?Key-Pair-Id=APKAIOCKYZS7WKBB6G7A&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jYy5mYW50aWEuanAvdXBsb2Fkcy9wb3N0X2NvbnRlbnRfcGhvdG8vZmlsZS80NTYzMzg5L21haW5fYTk3NjM0MjctM2NjZC00ZTUxLWJjZGUtZmY1ZTFjZTBhYTU2LmpwZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTY0NjkxMzk3OH19fV19&Signature=jyW5ankfO9uCHlKkozYU9RPpO3jzKTW2HuyXgS81i~cRgrXcI9orYU0IXuiit~0TznIyXbB7F~6Z790t7lX948PYAb9luYIREJC2u7pRMP3OBbsANbbFE0o4VR-6O3ZKbYQ4aG~ofVEZfiFVGoKoVtdJxj0bBNQV29eeFylGQATkFmywne1YMtJMqDirRBFMIatqNuunGsiWCQHqLYNHCeS4dZXlOnV8JQq0u1rPkeAQBmDCStFMA5ywjnWTfSZK7RN6RXKCAsMTXTl5X~I6EZASUPoGQy2vHUj5I-veffACg46jpvqTv6mLjQEw8JG~JLIOrZazKZR9O2kIoLNVGQ__

            # from file download:
            # https://cc.fantia.jp/uploads/post_content/file/1830956/cbcdfcbe_20220224_120_040_100.png?Key-Pair-Id=APKAIOCKYZS7WKBB6G7A&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9jYy5mYW50aWEuanAvdXBsb2Fkcy9wb3N0X2NvbnRlbnQvZmlsZS8xODMwOTU2L2NiY2RmY2JlXzIwMjIwMjI0XzEyMF8wNDBfMTAwLnBuZyIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTY0NjkxNDU4Nn19fV19&Signature=d1nw8gs9vcshIAeEH4oESm9-7z6y4A7MfoIRRvtUtV9iqTNA8KM0ORuCI7NwEoYc1VHsxy9ByeuSBpNaJoknnc3TOmHFhVRcLn~OWpnWqiHEPpMcSEG7uGlorysjEPmYYRGHjE7LJYcWiiJxjZ~fSBbYzxxwsjroPm-fyGUtNhdJWEMNp52vHe5P9KErb7M8tP01toekGdOqO-pkWm1t9xm2Tp5P7RWcbtQPOixgG4UgOhE0f3LVwHGHYJV~-lB5RjrDbTTO3ezVi7I7ybZjjHotVUK5MbHHmXzC1NqI-VN3vHddTwTbTK9xEnPMR27NHSlho3-O18WcNs1YgKD48w__
            #
            # products:
            # https://c.fantia.jp/uploads/product/image/249638/main_fd5aef8f-c217-49d0-83e8-289efb33dfc4.jpg
            # https://c.fantia.jp/uploads/product_image/file/219407/main_bd7419c2-2450-4c53-a28a-90101fa466ab.jpg (sample)
            # https://c.fantia.jp/uploads/product_image/file/219407/bd7419c2-2450-4c53-a28a-90101fa466ab.jpg
            case "uploads", image_type, ("file" | "image"), image_id, _filename:
                instance = FantiaImageUrl(parsable_url)
                instance.image_type = image_type
                instance.image_id = int(image_id)
                if image_type in ("post", "product"):
                    instance.post_id = int(image_id)
                else:
                    instance.post_id = None

                image_uuid = parsable_url.stem.split("_")[-1]
                if len(image_uuid) == 36:
                    instance.image_uuid = image_uuid
                else:
                    instance.image_uuid = None

            # https://fantia.jp/posts/343039/post_content_photo/1617547
            # https://fantia.jp/posts/1143951/download/1830956
            case "posts", post_id, ("download" | "post_content_photo") as image_type, image_id:
                instance = FantiaImageUrl(parsable_url)
                instance.image_type = image_type
                instance.image_id = int(image_id)
                instance.post_id = int(post_id)
                instance.image_uuid = None

            # https://fantia.jp/posts/1148334
            case ("posts" | "products") as post_type, post_id, *_:
                instance = FantiaPostUrl(parsable_url)
                instance.post_id = int(post_id.split("#")[0])
                instance.post_type = post_type

            # https://fantia.jp/fanclubs/64496
            # https://fantia.jp/fanclubs/1654/posts
            # https://job.fantia.jp/fanclubs/5734
            case "fanclubs", artist_id, *_:
                instance = FantiaFanclubUrl(parsable_url)
                instance.fanclub_id = int(artist_id)
                instance.fanclub_name = None

            # https://fantia.jp/asanagi
            # https://fantia.jp/koruri
            case username, :
                instance = FantiaFanclubUrl(parsable_url)
                instance.fanclub_name = username
                instance.fanclub_id = None

            # https://c.fantia.jp/uploads/fanclub/cover_image/319092/main_webp_40d41997-fa92-42fa-94d4-93bd9904db32.webp
            case "uploads", "fanclub", "cover_image", fanclub_id, _:
                instance = FantiaFanclubAssetUrl(parsable_url)
                instance.fanclub_id = int(fanclub_id)

            case _:
                return None

        return instance
