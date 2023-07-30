import requests
import json
from os import path
from utils import custom_print, get_content_type, get_file_data, MEDIA_CATEGORY


class ContentTooLong(requests.RequestException):
    """ LinkedIn post limit reached """
    pass


class LinkedIn:
    POST_CHAR_LIMIT     = 3000

    BASE_URL            = "https://www.linkedin.com"

    POST_ENDPOINT       = BASE_URL + "/voyager/api/contentcreation/normShares"
    UPLOAD_ENDPOINT     = BASE_URL + "/voyager/api/voyagerVideoDashMediaUploadMetadata?action=upload"

    def __init__(self, cookies):
        self.cookies = cookies
        self.headers = {
            "User-Agent"        : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "accept"            : "application/vnd.linkedin.normalized+json+2.1",
            "accept-language"   : "en-US,en;q=0.9",
            "content-type"      : "application/json; charset=UTF-8",
            "csrf-token"        : cookies["JSESSIONID"],
            "referrer-policy"   : "strict-origin-when-cross-origin, strict-origin-when-cross-origin",
            "origin"            : self.BASE_URL,
            "referrer"          : self.BASE_URL + "/feed/",
            "cookie"            : "li_at=%s; JSESSIONID=\"%s\"" % (cookies["li_at"], cookies["JSESSIONID"])
            # ... other headers ...
        }

    def post(self, text, media=None):

        if media is None:
            media = []

        payload = {
            "visibleToConnectionsOnly": False,
            "externalAudienceProviders": [],
            "commentaryV2": {
                "text": text,
                "attributes": []
            },
            "origin": "FEED",
            "allowedCommentersScope": "ALL",
            "postState": "PUBLISHED",
            "media": media
        }

        try:

            if len(text) > self.POST_CHAR_LIMIT:
                raise ContentTooLong()

            response = requests.post(self.POST_ENDPOINT, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            # Handle response

        except ContentTooLong:
            custom_print(f"Error posting to LinkedIn: post character limit reached")
        except requests.exceptions.RequestException as e:
            custom_print(f"Error posting to LinkedIn: {e}")

    def post_file(self, text, file_path_list=None):

        # TODO: find all mediaUploadType's. Determine use-case. Store in fs or stream?

        if file_path_list is None:
            file_path_list = []

        file_path = path.join(*file_path_list)

        fname = file_path_list[-1]
        fbinary, fsize, ftype = get_file_data( file_path, protocol="rb", incl_meta=True )

        payload = {
            "mediaUploadType": "IMAGE_SHARING",
            "fileSize": fsize,
            "filename": fname
        }

        content_type = get_content_type(file_path)

        if not content_type:
            return

        try:
            response = requests.post(self.UPLOAD_ENDPOINT, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()

            data                              = response.json()["data"]["value"]
            upload_endpoint                   = data["singleUploadUrl"]
            self.headers["media-type-family"] = data["singleUploadHeaders"]["media-type-family"]
            self.headers["content-type"]      = content_type

            response = requests.put(upload_endpoint, headers=self.headers, data=open(file_path, 'rb'))
            response.raise_for_status()

            # image is uploaded. now post.
            self.post(
                text,
                [
                    # video category has different keys
                    { "category": MEDIA_CATEGORY.IMAGE.name, "mediaUrn": data["urn"], "tapTargets": [] }
                ]
            )

        except requests.exceptions.RequestException as e:
            custom_print(f"Error posting to LinkedIn: {e}")
