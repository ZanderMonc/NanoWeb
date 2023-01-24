import time
import matplotlib.pyplot as plt

from nano import NanoDataManager


if __name__ == "__main__":
    start_time = time.time()
    data_manager = NanoDataManager("../data/matrix_scan02")
    data_manager.preload()
    # data_manager.load_all()
    end_time = time.time()
    print(f"Loading took {end_time - start_time} seconds")

    # create plot of first dataset of z vs time
    data_sets = list(data_manager.values)
    print(len(data_sets))
    for data_set in data_sets:

        segments = data_set.segments

        for i, segment in enumerate(segments):
            plt.plot(
                segment.z,
                segment.force,
                label="Segment " + str(i),
            )
    plt.show()
