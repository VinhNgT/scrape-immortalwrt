# This program is used to create checksums_xxh3_64.csv of the output files

import os
import xxhash

OUTPUT_DIR = "./output/"
HASH_FILE = "./checksums_xxh3_64.csv"


# Class to save hash info
class HashInfo:
    def __init__(self, filename: str, xxh3_64: str):
        self.filename = filename
        self.xxh3_64 = xxh3_64

    def __str__(self) -> str:
        return f"{self.filename},{self.xxh3_64}"

    def __repr__(self) -> str:
        return str(self)


# Function to generate hash of all files in OUTPUT_DIR using xxh3_64 algorithm
# and save it to checksums_xxh3_64.csv
def main():
    print("Generating hashes...")

    # Get all files in OUTPUT_DIR and it subdirectories
    files = []
    for root, dirs, filenames in os.walk(OUTPUT_DIR):
        for filename in filenames:
            files.append(os.path.join(root, filename)[len(OUTPUT_DIR) :])

    # Generate hashes
    hashes = []
    for id, file in enumerate(files):
        print(f"({id + 1} of {len(files)}) Generating hash of {file}...")
        with open(OUTPUT_DIR + file, "rb") as f:
            hashes.append(HashInfo(file, xxhash.xxh3_64(f.read()).hexdigest()))

    # Save hashes to file
    print("Saving hashes to file...")

    with open(HASH_FILE, "w") as f:
        f.write("\n".join([str(hash) for hash in hashes]))


if __name__ == "__main__":
    main()
