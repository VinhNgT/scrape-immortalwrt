# This program is used to download the images from the website

import csv
from distutils.util import strtobool
import os
import signal
import wget
import sys

OUTPUT_DIR = "./output/images/"
PROGRESS_FILE = "./get_images_progress.txt"


class LinkInfo:
    base_url = "https://downloads.immortalwrt.org/releases/18.06-SNAPSHOT/targets/"

    def __init__(
        self,
        rawLink: str,
        sha256sum: str,
        size: str,
        date: str,
        isFile: bool,
        isSupplementary: bool,
    ):
        self.rawLink = rawLink
        self.link = rawLink[len(self.base_url) :]
        self.sha256sum = sha256sum
        self.size = size
        self.date = date
        self.isFile = isFile
        self.isSupplementary = isSupplementary

    def __str__(self) -> str:
        return self.link

    def __repr__(self) -> str:
        return str(self)


completed_index = -1


def ctr_c_handler(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == "y":
        save_progress()
        exit(1)


signal.signal(signal.SIGINT, ctr_c_handler)


def save_progress():
    with open(PROGRESS_FILE, "w") as progress_file:
        progress_file.write(str(completed_index))


def main():
    global completed_index

    print("Getting current progress... ", end="")
    if len(sys.argv) == 2:
        completed_index = int(sys.argv[1])
    else:
        with open(PROGRESS_FILE, "r") as progress_file:
            completed_index = int(progress_file.readline())
    print(f"index {completed_index}")

    print("Loading urls...")
    rawData = list(csv.reader(open("scrape/18_06.csv")))[1:]
    data = list(
        map(
            lambda entry: LinkInfo(
                entry[0],
                entry[1],
                entry[2],
                entry[3],
                strtobool(entry[4]),
                strtobool(entry[5]),
            ),
            rawData,
        )
    )

    # Get images only
    data = list(filter(lambda entry: not entry.isSupplementary, data))

    print("Creating folders...")
    folder_urls = list(filter(lambda entry: not entry.isFile, data))

    for fo_url in folder_urls:
        path = OUTPUT_DIR + fo_url.link
        try:
            os.makedirs(path)
        except:
            pass

    print(f"Downloading files...")
    file_urls = list(filter(lambda entry: entry.isFile, data))

    for index, fi_url in enumerate(
        file_urls[(completed_index + 1) :], start=completed_index + 1
    ):
        print(
            f"Downloading index {index} ({index + 1} of {len(file_urls)}): {fi_url.link}"
        )
        save_file_dir = OUTPUT_DIR + fi_url.link

        if os.path.exists(save_file_dir):
            os.remove(save_file_dir)

        wget.download(fi_url.rawLink, save_file_dir)
        print()

        completed_index = index

        if index % 100 == 0:
            save_progress()

    save_progress()
    print("Done !")


if __name__ == "__main__":
    main()
