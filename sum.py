def squares(n=5):
    return [f"{i}:{i * i}" for i in range(1, n + 1)]


def name(n=5):
    for line in squares(n):
        print(line)


if __name__ == "__main__":
    name()
