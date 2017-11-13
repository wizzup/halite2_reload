# Usage: reload.py <filename> <player_id> <bot_path>
# Note that the replay file must be decompressed JSON (not zstd; use the Chlorine Viewer for this).

import json, subprocess, sys

# ------------------------------

def send(link, msg):
	if msg.endswith("\n") == False:
		msg += "\n"
	msg = bytes(msg, encoding = "ascii")
	link.stdin.write(msg)
	link.stdin.flush()

# ------------------------------

def send_frame(link, replay, n):

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

		if len(ship_id_strings) > 0:

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
	planet_id_strings = sorted(planets.keys(), key = lambda x : int(x))

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

		if planet["owner"] == None:
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

	send(link, final)

# ------------------------------

def main():

	filename = sys.argv[1]

	with open(filename) as infile:
		replay = json.loads(infile.read())

	link = subprocess.Popen(sys.argv[3], shell = False, stdin = subprocess.PIPE, stdout = subprocess.PIPE)

	pid = int(sys.argv[2])

	width, height = replay["width"], replay["height"]

	send(link, "{}".format(pid))
	send(link, "{} {}".format(width, height))

	send_frame(link, replay, 0)
	link.stdout.readline()			# The bot's init message e.g. its name

	for n in range(replay["num_frames"]):
		send_frame(link, replay, n)
		link.stdout.readline()
		if n % 10 == 0:
			print("Turn {}".format(n))

	print("Completed OK")

# ------------------------------

main()

