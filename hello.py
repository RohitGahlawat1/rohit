def build_list():
    items = [1, 2, 3, "h", "gf"]
    items[0] = 3
    return items


def main():
    print("hello")
    print(build_list()[4])


if __name__ == "__main__":
    main()
