from fastapi import HTTPException


class ControllerException(HTTPException): ...
