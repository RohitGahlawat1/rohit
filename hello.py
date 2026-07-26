def build_list():
    ls = [1, 2, 3, "h", "gf"]
    ls[0] = 3
    return ls


def main():
    print("hello")
    print(build_list()[4])


if __name__ == "__main__":
    main()
