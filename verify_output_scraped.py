# This program is used to verify the output of the scrape program
# It will check if the files in the output directory USING THE DOWNLOADED SHA256SUMS SCRAPED FROM THE WEBSITE

import csv
from distutils.util import strtobool
import hashlib
import os

OUTPUT_IMAGE_DIR = "./output/images/"
OUTPUT_SUPPLEMENTARIES_DIR = "./output/supplementaries/"


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


def is_empty(string):
    return not string.strip()


def check(urls, parent_path, extra_sha256sum_hash_map={}):
    not_found = []
    failed_sha256sum = []

    for id, url in enumerate(urls):
        sha256sum_from_hash_map = False

        path = parent_path + url.link
        print(f"({id + 1} of {len(urls)}) Checking {path}...", end=" ")

        if not os.path.isfile(path):
            not_found.append(url)
            print("not found")
            continue

        if is_empty(url.sha256sum):
            if url.link in extra_sha256sum_hash_map:
                url.sha256sum = extra_sha256sum_hash_map[url.link]
                sha256sum_from_hash_map = True
            else:
                print("empty sha256sum, skip")
                continue

        with open(path, "rb") as file:
            sha256sum = hashlib.sha256(file.read()).hexdigest()
            if sha256sum != url.sha256sum:
                failed_sha256sum.append(url)
                print("failed")
                continue

            if sha256sum_from_hash_map:
                print("passed using sha256sum hash map")
            else:
                print("passed")

    return (not_found, failed_sha256sum)


def print_results(not_found, failed_sha256sum):
    if len(not_found) == 0 and len(failed_sha256sum) == 0:
        print("\nAll pass !")
        return

    print(f"\nNot found {len(not_found)} file(s):")
    for id, url in enumerate(not_found):
        print(url.link)
        if id > 10:
            print("...")
            break

    print(f"\nFailed sha256sum {len(failed_sha256sum)} file(s):")
    for id, url in enumerate(failed_sha256sum):
        print(url.link)
        if id > 10:
            print("...")
            break


# Funtion to get all files named 'sha256sums' in the directory
def get_sha256sum_files(dir):
    sha256sum_files = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file == "sha256sums":
                sha256sum_files.append(os.path.join(root, file).replace("\\", "/"))

    return sha256sum_files


def get_sha256sum_from_line(line):
    line = line.strip().split(" ")
    return (line[0], line[1][1:])


# Function to build a hash map of all sha256sum_file
def build_sha256sum_file_hash_map(dir):
    sha256sum_file_hash_map = {}
    sha256sum_files = get_sha256sum_files(dir)
    for id, sha256sum_file in enumerate(sha256sum_files):
        sha256sum_file_parent = os.path.dirname(sha256sum_file).removeprefix(dir)

        with open(sha256sum_file, "r") as file:
            for line in file:
                sha256sum, filename = get_sha256sum_from_line(line)
                sha256sum_path = sha256sum_file_parent + "/" + filename
                sha256sum_file_hash_map[sha256sum_path] = sha256sum

    return sha256sum_file_hash_map


def main():
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

    print("Building sha256sum image files hash map...")
    sha256sum_from_files = build_sha256sum_file_hash_map(OUTPUT_IMAGE_DIR)

    print("Checking image files...")
    image_urls = list(
        filter(lambda entry: entry.isFile and not entry.isSupplementary, data)
    )
    img_check_result = check(image_urls, OUTPUT_IMAGE_DIR)
    # print_results(*img_check_result)

    print("Building sha256sum supplementary files hash map...")
    sha256sum_from_files = build_sha256sum_file_hash_map(OUTPUT_SUPPLEMENTARIES_DIR)

    print("Checking supplementary files...")
    supplementary_urls = list(
        filter(lambda entry: entry.isFile and entry.isSupplementary, data)
    )
    supplementary_check_result = check(
        supplementary_urls, OUTPUT_SUPPLEMENTARIES_DIR, sha256sum_from_files
    )
    # print_results(*supplementary_check_result)

    not_found = [*img_check_result[0], *supplementary_check_result[0]]
    failed_sha256sum = [*img_check_result[1], *supplementary_check_result[1]]
    print_results(not_found, failed_sha256sum)

    # Wait for user input to exit
    input("Press enter to exit...")


if __name__ == "__main__":
    main()
