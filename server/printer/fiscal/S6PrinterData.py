# server/printer/fiscal/S6PrinterData.py
class S6PrinterData:
    def __init__(self, data=None):
        self.raw_data = data
        self._parse(data)
    
    def _parse(self, data):
        if data:
            self.data = data
    
    def __repr__(self):
        return f"S6PrinterData({self.raw_data[:50] if self.raw_data else 'None'}...)"