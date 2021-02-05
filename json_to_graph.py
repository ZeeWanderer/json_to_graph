import matplotlib.pyplot as plt
import argparse
import json
import os
from os.path import join, dirname, abspath


def dir_path(path):
    if os.path.isdir(path) or os.path.isfile(path):
        return os.path.abspath(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def normalize_coordinates(vertices: list[dict], area_size):
    coord_space = area_size+1
    retval = list()
    for vertice in vertices:
        retval.append([vertice["column"], coord_space-vertice["row"]])
    return retval


def main():
    global workdir_path, raw_files, exec_path
    parser = argparse.ArgumentParser("json_to_graph")
    parser.add_argument('path', type=dir_path, help="path to directory containing jsons or path to json file.")

    args = parser.parse_args()

    exec_path = dirname(abspath(__file__))
    raw_files = []

    if os.path.isdir(args.path):
        workdir_path = args.path
        for dirpath, dirs, filenames in os.walk(args.path):
            for f in filenames:
                if f.endswith(".json"):
                    raw_files.append(os.path.abspath(os.path.join(dirpath, f)))
    else:
        raw_files.append(args.path)
        workdir_path = os.path.dirname(args.path)

    # process files
    for raw_f_path in raw_files:
        raw_json = None
        with open(raw_f_path, "r", encoding="utf8") as raw_f:
            try:
                raw_json = json.load(raw_f)
            except Exception as e:
                print(f"Json error: {raw_f_path}: {e}")
                continue
        area_size = int(raw_json["area_size"])
        vertices = normalize_coordinates(raw_json["vertices"], area_size)

        x_points, y_points = zip(*vertices)
        edges = raw_json["edges"]
        title = raw_json["title"]
        color = raw_json["color"]  # For now unused

        fig, ax = plt.subplots()

        for edge in edges:
            start = edge[0]
            end = edge[1]
            x_ = [x_points[start], x_points[end]]
            y_ = [y_points[start], y_points[end]]
            ax.plot(x_, y_, color="black")
        ax.scatter(x_points, y_points)

        for idx, vertice in zip(range(0, len(vertices)), vertices):
            ax.annotate(str(idx), vertice, fontsize=16, color="red")

        ax.set_title(title)
        fig.savefig(raw_f_path.replace(".json", ".png"))


if __name__ == '__main__':
    main()
