class PIVMask:
    def __init__(self, flag_dataset, mask_flag: int = 2):
        self._flag_dataset = flag_dataset
        self._mask_flag = mask_flag

    def sel(self, **coords):
        return self._flag_dataset.sel(**coords) & self._mask_flag == 0

    def isel(self, **coords):
        return self._flag_dataset.isel(**coords) & self._mask_flag == 0
