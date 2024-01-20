class H5PartialDump(Exception):
    def __init__(self, datasets: list):
        self.datasets = datasets
        super().__init__(f"The following datasets were not written to: {', '.join(self.datasets)}")
