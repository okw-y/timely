def parse(path: str) -> dict[str, str]:
    with open(path, mode="r", encoding="utf-8") as file:
        data = file.readlines()

    output = {}
    for line in data:
        line = line.strip()
        if line.startswith("//") or not line:
            continue

        output[line.split("=", 1)[0]] = line.split("=", 1)[1]

    return output
