#!/usr/bin/env nix-shell
#! nix-shell -p python3 -i python

# Usage: extract.py <filename> <player_id>
# Note that the replay file must be decompressed JSON (not zstd; use the Chlorine Viewer for this).

import json
import sys


class MoveList:

    # FIXME: currently assumes bot sends sane commands.

    def __init__(self, data):

        self.moves = dict()

        if type(data) is str:
            self.init_from_string(data)
        elif type(data) is dict:
            self.init_from_dict(data)


    # def init_from_string(self, s):
    #
    #     tokens = s.split()
    #
    #     acc = ""
    #     length = 0
    #
    #     for token in tokens:
    #
    #         if len(acc) > 0:
    #             acc += " "
    #
    #         if length == 3 and acc[0] == 't' and token[0] != '-':
    #             acc += str(int(token) % 360)                        # Relevant to my interests.
    #         else:
    #             acc += token
    #
    #         length += 1
    #
    #         if acc[0] == 't' and length == 4:
    #
    #             self.moves[int(acc.split()[1])] = acc
    #             acc = ""
    #             length = 0
    #
    #         elif acc[0] == 'd' and length == 3:
    #
    #             self.moves[int(acc.split()[1])] = acc
    #             acc = ""
    #             length = 0
    #
    #         elif acc[0] == 'u' and length == 2:
    #
    #             self.moves[int(acc.split()[1])] = acc
    #             acc = ""
    #             length = 0


    # def init_from_dict(self, d):
    #
    #     for key in d:
    #
    #         order = d[key]
    #
    #         cmd = order["type"][0]
    #         sid = order["shipId"]
    #
    #         if cmd == 'u':
    #
    #             self.moves[sid] = "{} {}".format(cmd, sid)
    #
    #         elif cmd == 't':
    #
    #             angle = order["angle"]
    #             if angle > 0:
    #                 angle %= 360
    #             mag = order["magnitude"]
    #             self.moves[sid] = "{} {} {} {}".format(cmd, sid, mag, angle)
    #
    #         elif cmd == 'd':
    #
    #             planet = order["planet_id"]
    #             self.moves[sid] = "{} {} {}".format(cmd, sid, planet)


    # def sids(self):
    #
    #     ret = set()
    #
    #     for key in self.moves:
    #         ret.add(key)
    #
    #     return ret

# ------------------------------

# def send(link, msg):
#     if msg.endswith("\n") == False:
#         msg += "\n"
#     msg = bytes(msg, encoding = "ascii")
#
#     link.stdin.write(msg)
#     link.stdin.flush()

# ------------------------------

def print_frame(replay, n):

    elements = []

    frame = replay["frames"][n]

    players = frame["ships"]
    player_id_strings = sorted(players.keys())

    elements.append(len(player_id_strings))

    for pid in player_id_strings:

        shipobj = players[pid]
        ship_id_strings = sorted(shipobj.keys(), key = lambda x : int(x))

        elements.append(pid)
        elements.append(len(ship_id_strings))

        for sid in ship_id_strings:

            ship = players[pid][sid]

            for key in ["id", "x", "y", "health", "vel_x", "vel_y"]:
                elements += [ship[key]]

            dockedstatus_number = {"undocked": 0, "docking": 1, "docked": 2, "undocking": 3}[ship["docking"]["status"]]

            elements.append(dockedstatus_number)

            if dockedstatus_number == 0:
                elements.append(0)
            else:
                elements.append(ship["docking"]["planet_id"])

            if dockedstatus_number not in [1,3]:
                elements.append(0)
            else:
                elements.append(ship["docking"]["turns_left"])

            elements.append(0)

    planets = frame["planets"]
    planet_id_strings = sorted(planets.keys(), key = lambda x: int(x))

    elements.append(len(planets))

    for plid in planet_id_strings:

        planet = planets[plid]

        elements.append(planet["id"])

        initial_planet = replay["planets"][int(planet["id"])]

        elements.append(initial_planet["x"])
        elements.append(initial_planet["y"])
        elements.append(planet["health"])
        elements.append(initial_planet["r"])
        elements.append(initial_planet["docking_spots"])
        elements.append(planet["current_production"])
        elements.append(planet["remaining_production"])

        if planet["owner"] is None:
            elements.append(0)
            elements.append(0)
        else:
            elements.append(1)
            elements.append(planet["owner"])

        elements.append(len(planet["docked_ships"]))

        for sid in planet["docked_ships"]:
            elements.append(sid)

    for i in range(len(elements)):
        elements[i] = str(elements[i])

    final = " ".join(elements)
    print(final)

# ------------------------------

def main():

    if len(sys.argv) < 2:
        print("Usage: extract.py <filename> <player_id>")
        return

    filename = sys.argv[1]

    with open(filename) as infile:
        replay = json.loads(infile.read())

    pid = int(sys.argv[2])

    width, height = replay["width"], replay["height"]

    print("{}".format(pid))
    print("{} {}".format(width, height))
    print_frame(replay, 0)

    for number in range(replay["num_frames"] - 1):
        print_frame(replay, number)

# ------------------------------

main()
