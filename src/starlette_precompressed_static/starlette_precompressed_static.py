from enum import Enum
from typing import List

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.responses import FileResponse, Response
from starlette.staticfiles import NotModifiedResponse, StaticFiles
from starlette.types import Scope


class Encoding(Enum):
    BROTLI = "br"
    GZIP = "gzip"


class PreCompressedStaticFiles(StaticFiles):
    def __init__(self, gzip=True, brotli=True, **kwargs):
        self.gzip = gzip
        self.brotli = brotli

        if kwargs.pop("html", False) is True:
            raise NotImplementedError("HTML mode not supported")

        super().__init__(**kwargs)

    async def get_response(self, org_path: str, scope: Scope) -> Response:

        request_headers = Headers(scope=scope)
        accepted_encodings = self.__get_accepted_encodings(
            request_headers.get("Accept-Encoding", "")
        )

        if self.brotli is True and Encoding.BROTLI.value in accepted_encodings:
            path = f"{org_path}.br"
            encoding = Encoding.BROTLI
        elif self.gzip is True and Encoding.GZIP.value in accepted_encodings:
            path = f"{org_path}.gz"
            encoding = Encoding.GZIP
        else:
            path = org_path
            encoding = None

        try:
            response = await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code == 404 and encoding is not None:
                # We may just be missing the compressed version.
                encoding = None
                response = await super().get_response(org_path, scope)
            else:
                raise

        if (
            isinstance(response, (FileResponse, NotModifiedResponse))
            and encoding is not None
        ):
            response.headers["Content-Encoding"] = encoding.value

        response.headers.add_vary_header("Accept-Encoding")

        return response

    @staticmethod
    def __get_accepted_encodings(accept_encoding: str) -> List[str]:
        """
        Parse the client's accepted encoding header.
        We ignore the client's preference here, unless
        it's zero.
        """
        accepted_encodings: List[str] = []
        for token in accept_encoding.split(","):
            identifiy_and_qvalue = token.split(";", 1)
            if len(identifiy_and_qvalue) == 2:
                qvalue = identifiy_and_qvalue[1].strip()
                if qvalue == "q=0":
                    continue
            identity = identifiy_and_qvalue[0].strip()
            accepted_encodings.append(identity)

        return accepted_encodings
