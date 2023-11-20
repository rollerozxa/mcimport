#!/bin/env python

import os
import stat
import sys
import logging
from block import *
import content
from pathlib import Path

logging.basicConfig(level=logging.INFO)

if (sys.version_info < (3, 0)):
	print("This script does not work with Python < 3.0, sorry.")
	exit(1)

if not Path(sys.argv[1]).exists():
	print("The provided minecraft world path does not exist.")
	exit(1)

if not Path(sys.argv[2]).exists():
	os.makedirs(sys.argv[2])

#if Path(sys.argv[2] +"/map.sqlite").exists():
#	print("A minetest world already exists - refusing to overwrite it.")
#	exit(1)

if not Path(sys.argv[2] + "/world.mt").exists():
	with open(sys.argv[2] + "/world.mt", "w") as wo:
		for backend in ['', 'player_', 'auth', 'mod_storage_']:
			wo.write(f"{backend}_backend = sqlite3\n")

		if os.environ["GAME_ID"] == "MTG":
			wo.write("gameid = minetest\n")
		elif os.environ["GAME_ID"] == "MCL2":
			wo.write("gameid = miniclonia\n")


if not Path(sys.argv[2] + "/worldmods").exists():
	os.makedirs(sys.argv[2]+"/worldmods")
if not Path(sys.argv[2] + "/worldmods/mcimport").exists():
	os.makedirs(sys.argv[2]+"/worldmods/mcimport")
if not Path(sys.argv[2]+"/worldmods/mcimport/init.lua").exists():
	with open(sys.argv[2]+"/worldmods/mcimport/init.lua", "w") as sn:
		sn.write("-- map conversion requires a special water level\n")
		sn.write("minetest.set_mapgen_params({water_level = -2})\n\n")
		sn.write("-- prevent overgeneration in incomplete chunks, and allow lbms to work\n")
		sn.write("minetest.set_mapgen_params({chunksize = 1})\n\n")
		sn.write("-- comment the line below if you want to enable mapgen (will destroy things!)\n")
		sn.write("minetest.set_mapgen_params({mgname = \"singlenode\"})\n\n")
		sn.write("\n\n")

if os.environ["GAME_ID"] == "MTG":
	if not Path(sys.argv[2]+"/get-mods.sh").exists():
		path = sys.argv[2]+"/get-mods.sh"
		with open(path, "w") as md:
					md.write('''\
#!/bin/sh

# run this script to automatically get all the required mods

mods=(
	https://codeload.github.com/minetest-mods/mesecons/zip/master,mesecons
	https://codeload.github.com/LNJ2/carpet/zip/master,carpet
	https://codeload.github.com/minetest-mods/crops/zip/master,crops
	https://codeload.github.com/minetest-mods/flowerpot/zip/master,flowerpot
	https://codeload.github.com/minetest-mods/lapis/zip/master,lapis
	https://codeload.github.com/minetest-mods/quartz/zip/master,quartz
	https://codeload.github.com/minetest-mods/xdecor/zip/master,xdecor
	https://codeload.github.com/oOChainLynxOo/hardenedclay/zip/master,hardenedclay
	https://codeload.github.com/minetest-mods/nether/zip/master,nether
	https://codeload.github.com/ShadowNinja/minetest_bedrock/zip/master,minetest_bedrock
	https://gitlab.com/VanessaE/basic_materials/-/archive/master/basic_materials-master.zip,basic_materials
	https://gitlab.com/VanessaE/biome_lib/-/archive/master/biome_lib-master.zip,biome_lib
	https://gitlab.com/VanessaE/plantlife_modpack/-/archive/master/plantlife_modpack-master.zip,plantlife_modpack
	https://gitlab.com/VanessaE/signs_lib/-/archive/master/signs_lib-master.zip,signs_lib
)

cd worldmods

for item in ${mods[@]} ; do
(
	url=$(echo $item | cut -d, -f1)
	mod=$(echo $item | cut -d, -f2)
	echo "Fetching: $mod"
	curl -q -L -o $mod.zip $url
	unzip -qq $mod.zip
	rm $mod.zip
	mv $mod-master $mod
	mv minetest_bedrock bedrock
)
done

# remove unneeded/unwanted submods
for ex in plantlife_modpack/dryplants plantlife_modpack/along_shore plantlife_modpack/molehills plantlife_modpack/woodsoils plantlife_modpack/bushes plantlife_modpack/bushes_classic plantlife_modpack/youngtrees plantlife_modpack/3dmushrooms plantlife_modpack/cavestuff plantlife_modpack/poisonivy plantlife_modpack/trunks; do
	echo "Pruning: $ex"
	rm -rf $ex
done
''')
	st = os.stat(path)
	os.chmod(path, st.st_mode | stat.S_IXUSR)


mcmap = MCMap(sys.argv[1])
mtmap = MTMap(sys.argv[2])

nimap, ct = content.read_content(["NETHER", "QUARTZ"])
mtmap.fromMCMap(mcmap, nimap, ct)
mtmap.save()

print("Conversion finished!\n")
if os.environ["GAME_ID"] == "MTG":
	print("Run \"sh get-mods.sh\" in the new world folder to automatically download all required mods.")
