
from pydantic import BaseModel, create_model, ConfigDict
from datetime import date, datetime
from typing import List, Union

class UfoObservation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # fields from the observation
    obs_id : str
    obs_posted : date
    obs_city : Union[str, None]
    obs_state : Union[str, None]
    obs_country : Union[str, None]
    obs_shape : Union[str, None]
    obs_duration : Union[str, None]
    obs_images : bool

    # fields from the details of the observation
    obs_ocurred : datetime
    obs_reported : datetime
    obs_summary : Union[str, None]
    obs_detailed_description : Union[str, None]

class UfoObservationList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observations : List[UfoObservation]