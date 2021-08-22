# OsrsBestInSlotScaper
Scrapes the OSRS wiki for items that are best in slot at a list of bosses.

Running the script without any command line arguments, will scrape every boss and output the best in slot gear for each one.
```buildoutcfg
$python src/main.py
```

If you're only interest in certain items, you can query them with the `--items-of-interest` option.

You can search multiple items, but make sure to surround items that are made up of multiple words with quotes.

```shell
python src\main.py --items-of-interest "dragon claws" "twisted bow" rapier --no-print-bosses
```

```text
...
Dragon claws is best in slot at 15 bosses.
- Grotesque Guardians
- Thermonuclear smoke devil
- Cerberus
- Abyssal Sire
- Alchemical Hydra
- Chaos Elemental
- Callisto
- The Mimic
- Giant Mole
- Sarachnis
- K'ril Tsutsaroth
- Vorkath
- Corporeal Beast
- Theatre of Blood
- Barrows
...
```

Additionally, if you're only interested in specific bosses, you can use the `--bosses-of-interest` option.

You can include multiple bosses separated by spaces. If the boss is multiple words, make sure you surround the boss with quotes.

```shell
python src/main.py --bosses-of-interest zulrah vorkath "commander ziliana" --no-print-items
```

```text
Best in slot gear for Commander Zilyana:
Rank 1:
Head:
- Armadyl helmet
Neck:
- Necklace of anguish
Back:
- Ava's assembler
Body:
- Armadyl chestplate
Legs:
- Armadyl chainskirt
Weapon:
- Twisted bow
Shield:
- Twisted buckler
Ammo/Spell:
- Dragon arrow
Gloves:
- Barrows gloves
Boots:
- Pegasian boots
Ring:
- Ring of suffering (i)
Special attack:
- Toxic blowpipe
```
