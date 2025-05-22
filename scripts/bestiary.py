import pygame
import json
import os

class Creature:
    """ defines the creature """
    def __init__(self, data):
        self.id = data["ID"]
        self.common_name = data["common_name"]
        self.species_name = data["species_name"]
        self.summary = data["summary"]
        self.skills_gained = data["skills_gained"]
        self.facts = data["facts"]
        self.locations_found = data["locations_found"]
        self.difficulty = data["difficulty"]
        self.danger = data["danger"]
        self.rarity = data["rarity"]
        self.sprite_path = data["sprite_path"]
        self.sprite = None
        
        self.load_sprite()

    def load_sprite(self):
        self.sprite = pygame.image.load(self.sprite_path)

class BestiaryEntry:
    def __init__(self, creature: Creature):
        self.creature = creature
        self.discovered = False
        self.kills = 0

    def discover(self):
        self.discovered = True
        self.kills += 1

    def rediscover(self):
        self.kills += 1

class Bestiary:
    def __init__(self, data_path="resources/dicts/bestiary.json", save_path="saves/Test/bestiary.json"):
        self.data_path = data_path
        self.save_path = save_path
        self.creatures = {}
        self.entries = {}
        self.load_creatures()
        self.load_progress()

    def load_creatures(self):
        with open(self.data_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            for creature_data in data["creatures"]:
                creature = Creature(creature_data)
                self.creatures[creature.id] = creature

    def load_progress(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r', encoding="utf-8") as file:
                saved_data = json.load(file)
                for creature_id, data in saved_data.items():
                    creature = self.creatures.get(creature_id)
                    if creature:
                        entry = BestiaryEntry(creature)
                        entry.discovered = data.get("discovered", False)
                        entry.kills = data.get("kills", 0)
                        self.entries[creature_id] = entry
        # Add Undiscovered Creatures
        for creature_id, creature in self.creatures.items():
            if creature_id not in self.entries:
                self.entries[creature_id] = BestiaryEntry(creature)

    def save_progress(self):
        data = {
            creature_id: {
                "discovered": entry.discovered,
                "kills": entry.kills
            }
            for creature_id, entry in self.entries.items()
        }
        with open(self.save_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    
    def discover_creature(self, creature_id):
        if creature_id in self.entries:
            entry = self.entries[creature_id]
            if not entry.discovered:
                entry.discover()
                print(f"New Creature Discovered: {entry.creature.common_name}")
            else:
                entry.rediscover()
                print(f"You reincountered {entry.creature.common_name} again")

        else:
            print(f"Unknown Creature ID: {creature_id}")