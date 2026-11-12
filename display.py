from tabulate import tabulate


def print_table(rows, title=None):
    if title:
        print(f"\n--- {title} ---")
    if not rows:
        print("No results.")
        return
    print(tabulate(rows, headers="keys", tablefmt="grid"))
