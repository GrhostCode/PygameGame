import json
def extract_json():
    def squash_manual(value, decimals=3):
        toPrint = []
        value = str(value)
        decimalsCount = 0
        decimalsCountExists = False
        escape = False
        for char in value:
            if (char != ".") & (escape == False):
                if decimalsCountExists:
                    if decimalsCount < decimals:
                        decimalsCount += 1
                        escape = True
                    else:
                        decimalsCount = 0
                toPrint.append(char)

            elif char == ".":
                toPrint.append(".")
                decimalsCountExists = True
        result = "".join(str(x) for x in toPrint)
        return float(result)

    def read(file):
        with open(file, "r") as file:
            return file.read()

    raw = read("plrSave.json")

    speeds = []
    for line in raw.splitlines():
        obj = json.loads(line)
        speeds.append(squash_manual(obj["speed"], 3))

    return sorted(speeds)
extract_json()
