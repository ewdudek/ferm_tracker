import datetime
import json

class FermPoint:
    def __init__(self):
        self.fermTemp = -1
        self.ambTemp = -1
        self.color = "Unknown"
        self.gravity = -1
        self.humidity = -1
        self.timestamp = datetime.datetime.now()
        #self._lock = threading.Lock()
    
    def __copy__(self):
        cls = self.__class__
        retcpy = cls.__new__(cls)
        retcpy.__dict__.update(self.__dict__)
        return retcpy
    
    def updateFermPoint(self, newColor, newFermTemp, newAmbTemp, newGravity, newHumidity, newTimestamp):
        #with self._lock:
        self.color = newColor
        self.fermTemp = newFermTemp
        self.ambTemp = newAmbTemp
        self.gravity = newGravity
        self.humidity = newHumidity
        self.timestamp = newTimestamp
    
    def _tryJSON(self, o):
        try:
            return o.__dict__
        except:
            return str(o)
    def toJSON(self):
        return json.dumps(self, default=lambda o: self._tryJSON(o), sort_keys=True, indent=4)
    
    def getColor(self):
        return self.color
    def getFermTemp(self):
        return self.fermTemp
    def getAmbTemp(self):
        return self.ambTemp
    def getGravity(self):
        return self.gravity
    def getHumidity(self):
        return self.humidity
    def getTimestamp(self):
        return self.timestamp
