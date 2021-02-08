import matplotlib.pyplot as plt
import numpy as np
import argparse
import json
import os
from os.path import join, dirname, abspath


def dir_path(path):
    if os.path.isdir(path) or os.path.isfile(path):
        return os.path.abspath(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def normalize_coordinates(vertices: list[dict], area_size, convert_to_positive=False):
    coord_space = area_size+1
    retval = list()
    for vertice in vertices:
        y_coord = coord_space-vertice["row"] if convert_to_positive else -vertice["row"]
        retval.append([vertice["column"], y_coord])
    return retval


def main():
    global workdir_path, raw_files, exec_path
    parser = argparse.ArgumentParser("json_to_graph")
    parser.add_argument('path', type=dir_path, help="path to directory containing jsons or path to json file, skipping")

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

        # VERIFICATION
        # verify area_size
        max_coord = max(max(x_points), max(y_points))
        if max_coord != area_size:
            print(f"Json warning: {raw_f_path}: Maximum coordinate {max_coord} > area_size - area_size mismatch")

        # verify edges
        tmp = set([frozenset(edge) for edge in edges])
        if len(tmp) != len(edges):
            print(f"Json warning: {raw_f_path}: Duplicate edges detected")
        for t in tmp:
            if len(t) != 2:
                print(f"Json warning: {raw_f_path}: Loop edge detected")

        try:
            for edge in edges:
                for vertex in edge:
                    if not vertex < len(vertices):
                        print(f"Json error: {raw_f_path}: Edge vertex index is out of bounds: {edge},"
                              f" {vertex} > {len(vertices)-1}, skipping")
                        raise Exception("error")
        except:
            continue

        # PLOTTING
        fig, ax = plt.subplots()

        for edge in edges:
            start = edge[0]
            end = edge[1]
            x_ = [x_points[start], x_points[end]]
            y_ = [y_points[start], y_points[end]]
            ax.plot(x_, y_, color="black")
        ax.scatter(x_points, y_points)
        
        plt.xticks(np.arange(0, area_size + 1, step=1))
        plt.yticks(np.arange(0, -area_size - 1, step=-1))

        for idx, vertice in zip(range(0, len(vertices)), vertices):
            ax.annotate(str(idx), vertice, fontsize=16, color="red")

        ax.set_title(title)
        fig.savefig(raw_f_path.replace(".json", ".png"))


if __name__ == '__main__':
    main()
