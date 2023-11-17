import csv


def save_to_csv(path, **kwargs):
    with open(path, 'w', encoding='utf_8_sig', newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(kwargs.keys())
        data = list(kwargs.values())
        data = list(zip(*data))
        csv_writer.writerows(data)
