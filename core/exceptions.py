class ExamAutomationError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details

class ExcelImportError(ExamAutomationError): pass
class PDFGenerationError(ExamAutomationError): pass
class AllocationError(ExamAutomationError): pass  
class ValidationError(ExamAutomationError): pass
class DatabaseError(ExamAutomationError): pass
class ConfigurationError(ExamAutomationError): pass
