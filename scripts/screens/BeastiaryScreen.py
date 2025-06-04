from math import ceil

import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat


from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import (
    UISpriteButton,
    UIImageButton,
    UITextBoxTweaked,
)
from scripts.utility import get_text_box_theme, scale, get_alive_status_cats, shorten_text_to_fit, get_living_clan_cat_count
from .Screens import Screens
from ..conditions import get_amount_cat_for_one_medic, medical_cats_condition_fulfilled


class BeastiaryScreen(Screens):
    current_page = 1
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.all_pages = []
        self.full_beast_list = []
        self.current_beasts_list = []
        self.help_button = None
        self.last_page = None
        self.next_page = None
        self.back_button = None
        with open(f"resources/dicts/beast.json", "r") as read_file:
            self.BEAST_LIST = ujson.loads(read_file.read())
        print(str(self.BEAST_LIST["CROW"]["summary"]))

        self.herbs = {}

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.next_page:
                self.current_page += 1
                print("next page")
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                print("last page")
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen("profile screen")

    def screen_switches(self):
        self.hide_menu_buttons()
        print(Beast.__init__(self))
        self.back_button = UIImageButton(
            scale(pygame.Rect((50, 50), (210, 60))),
            "",
            object_id="#back_button",
            manager=MANAGER,
        )
        self.next_creature = UIImageButton(
            scale(pygame.Rect((1290, 556), (68, 68))),
            "",
            object_id="#arrow_right_button",
            manager=MANAGER,
        )
        self.last_creature = UIImageButton(
            scale(pygame.Rect((1200, 556), (68, 68))),
            "",
            object_id="#arrow_left_button",
            manager=MANAGER,
        )
        self.crow = pygame_gui.elements.UIImage(
                scale(pygame.Rect((280, 880), (150, 150))),
                pygame.image.load("sprites/beasts/" + str(self.BEAST_LIST["CROW"]["sprite"])).convert_alpha(),
                manager=MANAGER,
            )
        if game.clan.game_mode != "classic":
            self.help_button = UIImageButton(
                scale(pygame.Rect((1450, 50), (68, 68))),
                "",
                object_id="#help_button",
                manager=MANAGER,
                tool_tip_text="Your medicine cats will gather herbs over each timeskip and during any patrols you send "
                "them on. You can see what was gathered in the Log below! Your medicine cats will give"
                " these to any hurt or sick cats that need them, helping those cats to heal quicker."
                "<br><br>"
                "Hover your mouse over the medicine den image to see what herbs your Clan has!",
            )
            self.last_page = UIImageButton(
                scale(pygame.Rect((660, 1272), (68, 68))),
                "",
                object_id="#arrow_left_button",
                manager=MANAGER,
            )
            self.next_page = UIImageButton(
                scale(pygame.Rect((952, 1272), (68, 68))),
                "",
                object_id="#arrow_right_button",
                manager=MANAGER,
            )
            self.cat_bg = pygame_gui.elements.UIImage(
                scale(pygame.Rect((280, 880), (1120, 400))),
                pygame.image.load("resources/images/sick_hurt_bg.png").convert_alpha(),
                manager=MANAGER,
            )
            self.cat_bg.disable()
 

        self.draw_med_den()

    def update_beasts(self):
        """
        set tab showing as either self.in_den_cats, self.out_den_cats, or self.minor_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 20.0))
            if len(self.current_listed_cats) > 20
            else 1
        )
        if self.current_page > self.all_pages:
            self.current_page = self.all_pages
        elif self.current_page < 1:
            self.current_page = 1

        self.current_page = max(1, min(self.current_page, len(self.all_pages)))

        # Check for empty list (no cats)
        if self.all_pages:
            self.display_cats = self.all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(self.all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(self.all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

    def draw_med_den(self):
        sorted_dict = dict(sorted(game.clan.herbs.items()))
        herbs_stored = sorted_dict.items()
        herb_list = []
        for herb in herbs_stored:
            amount = str(herb[1])
            type = str(herb[0].replace("_", " "))
            herb_list.append(f"{amount} {type}")
        if not herbs_stored:
            herb_list.append("Empty")
        if len(herb_list) <= 10:
            herb_display = "<br>".join(sorted(herb_list))

            self.den_base = UIImageButton(
                scale(pygame.Rect((216, 190), (792, 448))),
                "",
                object_id="#med_cat_den_hover",
                tool_tip_text=herb_display,
                manager=MANAGER,
            )
        else:
            count = 1
            holding_pairs = []
            pair = []
            added = False
            for y in range(len(herb_list)):
                if (count % 2) == 0:  # checking if count is an even number
                    count += 1
                    pair.append(herb_list[y])
                    holding_pairs.append("   -   ".join(pair))
                    pair.clear()
                    added = True
                    continue
                else:
                    pair.append(herb_list[y])
                    count += 1
                    added = False
            if added is False:
                holding_pairs.extend(pair)

            herb_display = "<br>".join(holding_pairs)
            self.den_base = UIImageButton(
                scale(pygame.Rect((216, 190), (792, 448))),
                "",
                object_id="#med_cat_den_hover_big",
                tool_tip_text=herb_display,
                manager=MANAGER,
            )

        herbs = game.clan.herbs
        for herb in herbs:
            if herb == "cobwebs":
                self.herbs["cobweb1"] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((216, 190), (792, 448))),
                    pygame.transform.scale(
                        pygame.image.load(
                            "resources/images/med_cat_den/cobweb1.png"
                        ).convert_alpha(),
                        (792, 448),
                    ),
                    manager=MANAGER,
                )
                if herbs["cobwebs"] > 1:
                    self.herbs["cobweb2"] = pygame_gui.elements.UIImage(
                        scale(pygame.Rect((216, 190), (792, 448))),
                        pygame.transform.scale(
                            pygame.image.load(
                                "resources/images/med_cat_den/cobweb2.png"
                            ).convert_alpha(),
                            (792, 448),
                        ),
                        manager=MANAGER,
                    )
                continue
            self.herbs[herb] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((216, 190), (792, 448))),
                pygame.transform.scale(
                    pygame.image.load(
                        f"resources/images/med_cat_den/{herb}.png"
                    ).convert_alpha(),
                    (792, 448),
                ),
                manager=MANAGER,
            )

    def exit_screen(self):
        self.last_creature.kill()
        self.next_creature.kill()
        self.crow.kill()
        self.den_base.kill()
        for herb in self.herbs:
            self.herbs[herb].kill()
        self.herbs = {}
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.clear_cat_buttons()

    def chunks(self, L, n):
        return [L[x : x + n] for x in range(0, len(L), n)]

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        for button in self.conditions_hover:
            self.conditions_hover[button].kill()
        for x in range(len(self.cat_names)):
            self.cat_names[x].kill()

        self.cat_names = []
        self.cat_buttons = {}
class Beast:
    """defines the beast"""
    common_name = None
    species_name = None
    summary = None
    skills_gained = ()
    facts = None
    discovered_beasts = ()
    all_beasts = ()
    discovered_status = False
    def beast_assign_discovery(self):
        print("function activated")
        if Beast.discovered_status:
            Beast.discovered_beasts.append(Beast.common_name)
        else:
            pass
        if Beast.discovered_beasts in Beast.all_beasts:
            print("discovered beasts in all beasts error check confirmed")
        else:
            print("extra discovered beast has been added. something went wrong")
        if Beast.all_beasts not in Beast.discovered_beasts:
            print("this will either signify not all beasts have been discovered OR ... work properly and be that if not discovered,")
            print("then do whatever is in here. eek")
        return Beast.discovered_status
        

