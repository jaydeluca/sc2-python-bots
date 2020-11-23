# Starcraft 2 Python Bots

Based on the [python-sc2](https://github.com/BurnySc2/python-sc2) framework.  

## Preparing your environment

First you will need to prepare your environment.

### Prerequisites

* Python 3.7.X +

##### Starcraft 2

On Windows SC2 is installed through the Battle.net app.  
Linux users can either download the Blizzard SC2 Linux package [here](https://github.com/Blizzard/s2client-proto#linux-packages) or, alternatively, set up Battle.net via WINE using this [lutris script](https://lutris.net/games/battlenet/).

SC2 should be installed in the default location. Otherwise (and for Linux) you might need to create the SC2PATH environment variable to point to the SC2 install location.

##### Starcraft 2 Maps

Download the Starcraft 2 Maps from [here](https://github.com/Blizzard/s2client-proto#map-packs).   For this tutorial you will at least need the 'Melee' pack.  
The maps must be copied into the **root** of the Starcraft 2 maps folder - default location: `C:\Program Files (x86)\StarCraft II\Maps`.

## Setup
Create and activate a virtual environment, install and run:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ./run.py --ComputerRace "Protoss" --ComputerDifficulty "Hard"
```
If all is well, you should see SC2 load and your bot start mining minerals.  
You can close the SC2 window to stop your bot running. 

## Updating your bot

### Bot name and race

Now you will want to name your bot and select its race.
You can specify both of these in the [bot/bot.py](bot/bot.py) file, in the `CompetitiveBot` class.

### Adding new code

As you add features to your bot make sure all your new code files are in the `bot` folder. This folder is included when creating the ladder.zip for upload to the bot ladders.

## Competing with your bot

To compete with your bot, you will first need zip up your bot, ready for distribution.   
You can do this using the `create_ladder_zip.py` script like so:
```
python create_ladder_zip.py
```
This will create the zip file`publish\bot.zip`.
You can then distribute this zip file to competitions.

# Troubleshooting

_to be filled in_