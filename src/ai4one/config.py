import tomllib


def load_config(
    path: str,
):
    with open(path, mode="rb") as f:
        return tomllib.load(f)
