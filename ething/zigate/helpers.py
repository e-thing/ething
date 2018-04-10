# coding: utf-8
from future.utils import string_types, integer_types



models = {}
    
    
clusterNames = {
    "0000" : "General: Basic",
    "0001" : "General: Power Config",
    "0002" : "General: Temperature Config",
    "0003" : "General: Identify",
    "0004" : "General: Groups",
    "0005" : "General: Scenes",
    "0006" : "General: On/Off",
    "0007" : "General: On/Off Config",
    "0008" : "General: Level Control",
    "0009" : "General: Alarms",
    "000A" : "General: Time",
    "000F" : "General: Binary Input Basic",
    "0020" : "General: Poll Control",
    "0019" : "General: OTA",
    "0101" : "General: Door Lock",
    "0201" : "HVAC: Thermostat",
    "0202" : "HVAC: Fan Control",
    "0300" : "Lighting: Color Control",
    "0400" : "Measurement: Illuminance",
    "0402" : "Measurement: Temperature",
    "0406" : "Measurement: Occupancy Sensing",
    "0500" : "Security & Safety: IAS Zone",
    "0702" : "Smart Energy: Metering",
    "0B05" : "Misc: Diagnostics",
    "1000" : "ZLL: Commissioning"
}


def clusterIdToName (cluster):
    if isinstance(cluster, integer_types):
        cluster = format('X', cluster)
    return clusterNames.get(cluster.rjust(4,'0').upper(), '')


# decorator: register a model
def model(models_, name):
    
    if isinstance(models_, string_types):
        models_ = [models_]
    
    def d(cls):
        
        for model in models_:
            models[model] = {
                'model': model,
                'name': name,
                'cls': cls
            }
        
        return cls
    return d


def model_info (model):
    
    return models.get(model)









