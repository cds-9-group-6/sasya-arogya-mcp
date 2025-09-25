class Farmer:
    def __init__(self, name: str, state: str, land_area: float, crop: str):
        """
        Initialize a Farmer instance.

        :param name: Name of the farmer
        :param state: State where the farmer resides
        :param land_area: Land area owned by the farmer (in acres or hectares)
        :param crop: Crop cultivated by the farmer
        """
        self.name = name
        self.state = state
        self.land_area = land_area
        self.crop = crop

    def __str__(self):
        """
        Return a string representation of the farmer.
        """
        return f"Farmer(name={self.name}, state={self.state}, land_area={self.land_area}, crop={self.crop})"

    def update_crop(self, new_crop: str):
        """
        Update the crop cultivated by the farmer.

        :param new_crop: New crop to be cultivated
        """
        self.crop = new_crop
