
from pydantic import BaseModel
from datetime import date

class UfoObservation(BaseModel):
    # fields from the observation
    obs_id : str
    obs_posted : date
    obs_city : str
    obs_state : str
    obs_country : str
    obs_shape : str
    obs_duration : str
    obs_images : bool

    # fields from the details of the observation
    obs_ocurred : date
    obs_reporetd : date
    obs_summary : str
    obs_detailed_description : str
