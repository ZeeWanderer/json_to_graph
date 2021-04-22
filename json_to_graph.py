import argparse
import json
import os
from os.path import dirname, abspath

import matplotlib.pyplot as plt
import numpy as np

from log import *


def dir_path(path):
    if os.path.isdir(path) or os.path.isfile(path):
        return os.path.abspath(path)
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def normalize_coordinates(vertices: list[dict], area_size, convert_to_positive=False):
    coord_space = area_size + 1
    retval = list()
    for vertice in vertices:
        y_coord = coord_space - vertice["row"] if convert_to_positive else -vertice["row"]
        retval.append([vertice["column"], y_coord])
    return retval


def main():
    global workdir_path, raw_files, exec_path

    os.system('color')

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
                log_error(f"Json error: {raw_f_path}: {e}")
                log_notice(f"Skipping {raw_f_path}")
                continue

        area_size = int(raw_json["area_size"])
        vertices = normalize_coordinates(raw_json["vertices"], area_size)

        x_points, y_points = zip(*vertices)

        edges: list[list[int]] = raw_json["edges"]
        title: str = raw_json["title"]
        color: str = raw_json["color"]  # For now unused

        # VERIFICATION
        # verify area_size
        max_coord = max(max(x_points), max(y_points))
        if max_coord != area_size:
            log_warning(f"Json warning: {raw_f_path}: "
                        f"area_size mismatch: maximum coordinate {max_coord} > area_size")

        # verify edges
        list_of_edge_sets = [frozenset(edge) for edge in edges]
        set_of_edge_sets = set(list_of_edge_sets)
        if len(set_of_edge_sets) != len(edges):
            duplicate = list()
            for edge_set in list_of_edge_sets:
                edge = list(edge_set)
                if list_of_edge_sets.count(edge_set) > 1 and edge not in duplicate:
                    duplicate.append(edge)
            log_warning(f"Json warning: {raw_f_path}: Duplicate edges {duplicate} detected")
        for edge_set in set_of_edge_sets:
            if len(edge_set) != 2:
                loop_vertex = next(iter(edge_set))
                log_error(f"Json warning: {raw_f_path}: Loop edge [{loop_vertex}, {loop_vertex}] detected")

        try:
            for edge in edges:
                for vertex in edge:
                    if not 0 <= vertex < len(vertices):
                        log_error(f"Json error: {raw_f_path}: Edge vertex index is out of bounds: {edge},"
                                  f" {vertex} is not in [0,{len(vertices)})")
                        raise Exception("error")
        except:
            log_notice(f"Skipping {raw_f_path}")
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
        plt.close(fig)


if __name__ == '__main__':
    main()
