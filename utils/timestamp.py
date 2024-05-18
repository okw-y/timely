from peewee import Model


def selectByDeltaType(type: str, model: type[Model]) -> tuple[list[tuple[str, int]], dict[str, object]]:
    output, applications = {}, {}
    for application in sorted(list(model.select()), reverse=True, key=lambda value: value.timestamp):
        time, date = "_", application.timestamp
        if type == "year":
            time = f"{date.year}"
        if type == "month":
            time = f"{date.month}.{date.year}"
        if type == "day":
            time = f"{date.day}.{date.month}.{date.year}"

        if time not in output:
            output[time] = 0

        output[time] += application.spent

        if time not in applications:
            applications[time] = []

        applications[time].append(
            (application.path, application.spent)
        )

    for key, value in applications.items():
        applications[key] = sorted(
            value, reverse=True, key=lambda chunk: chunk[1]
        )

    return list(output.items()), applications
