from fastapi import HTTPException, status

class BusinessException(HTTPException):
    
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class GoogleCalendarError(BusinessException):
    
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
