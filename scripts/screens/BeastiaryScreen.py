import pygame
import pygame_gui

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
    cat_buttons = {}
    conditions_hover = {}
    cat_names = []

    def __init__(self, name=None):
        super().__init__(name)
        self.help_button = None
        self.log_box = None
        self.log_title = None
        self.log_tab = None
        self.cats_tab = None
        self.hurt_sick_title = None
        self.display_med = None
        self.beast = None
        self.minor_tab = None
        self.out_den_tab = None
        self.in_den_tab = None
        self.injured_and_sick_cats = None
        self.minor_cats = None
        self.out_den_cats = None
        self.in_den_cats = None
        self.current_creature = None
        self.cat_bg = None
        self.last_page = None
        self.next_page = None
        self.last_creature = None
        self.next_creature = None
        self.den_base = None
        self.beast_info = None
        self.beast_name = None
        self.current_page = None
        self.beasts = None
        self.back_button = None

        self.tab_showing = self.in_den_tab
        self.tab_list = self.in_den_cats

        self.herbs = {}

        self.open_tab = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.next_page:
                self.current_page += 1
                self.update_sick_cats()
            elif event.ui_element == self.last_page:
                self.current_page -= 1
                self.update_sick_cats()
            elif event.ui_element == self.in_den_tab:
                self.in_den_tab.disable()
                self.tab_showing.enable()
                self.tab_list = self.in_den_cats
                self.tab_showing = self.in_den_tab
                self.update_sick_cats()
            elif event.ui_element == self.out_den_tab:
                self.tab_showing.enable()
                self.tab_list = self.out_den_cats
                self.tab_showing = self.out_den_tab
                self.out_den_tab.disable()
                self.update_sick_cats()
            elif event.ui_element == self.minor_tab:
                self.tab_showing.enable()
                self.tab_list = self.minor_cats
                self.tab_showing = self.minor_tab
                self.minor_tab.disable()
                self.update_sick_cats()
            elif event.ui_element in self.cat_buttons.values():
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen("profile screen")
            elif event.ui_element == self.beast:
                cat = event.ui_element.return_cat_object()
                game.switches["cat"] = cat.ID
                self.change_screen("profile screen")
            elif event.ui_element == self.cats_tab:
                self.open_tab = "cats"
                self.cats_tab.disable()
                self.log_tab.enable()
                self.handle_tab_toggles()
            elif event.ui_element == self.log_tab:
                self.open_tab = "log"
                self.log_tab.disable()
                self.cats_tab.enable()
                self.handle_tab_toggles()

    def screen_switches(self):
        self.hide_menu_buttons()
        Beast.assign_beast_info(self, beast_chosen="crow")
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

            self.hurt_sick_title = pygame_gui.elements.UITextBox(
                "Hurt & Sick Cats",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"),
                manager=MANAGER,
            )
            self.log_title = pygame_gui.elements.UITextBox(
                "Medicine Den Log",
                scale(pygame.Rect((281, 820), (400, 60))),
                object_id=get_text_box_theme("#text_box_40_horizcenter"),
                manager=MANAGER,
            )
            self.log_title.hide()
            self.cat_bg = pygame_gui.elements.UIImage(
                scale(pygame.Rect((280, 880), (1120, 400))),
                pygame.image.load("resources/images/sick_hurt_bg.png").convert_alpha(),
                manager=MANAGER,
            )
            self.cat_bg.disable()
            log_text = game.herb_events_list.copy()
            """if game.settings["fullscreen"]:
                img_path = "resources/images/spacer.png"
            else:
                img_path = "resources/images/spacer_small.png"""
            self.log_box = pygame_gui.elements.UITextBox(
                f"{f'<br>-------------------------------<br>'.join(log_text)}<br>",
                scale(pygame.Rect((300, 900), (1080, 360))),
                object_id="#text_box_26_horizleft_verttop_pad_14_0_10",
                manager=MANAGER,
            )
            self.log_box.hide()
            self.cats_tab = UIImageButton(
                scale(pygame.Rect((218, 924), (70, 150))),
                "",
                object_id="#hurt_sick_cats_button",
                manager=MANAGER,
            )
            self.cats_tab.disable()
            self.log_tab = UIImageButton(
                scale(pygame.Rect((218, 1104), (70, 128))),
                "",
                object_id="#med_den_log_button",
                manager=MANAGER,
            )
            self.in_den_tab = UIImageButton(
                scale(pygame.Rect((740, 818), (150, 70))),
                "",
                object_id="#in_den_tab",
                manager=MANAGER,
            )
            self.in_den_tab.disable()
            self.out_den_tab = UIImageButton(
                scale(pygame.Rect((920, 818), (224, 70))),
                "",
                object_id="#out_den_tab",
                manager=MANAGER,
            )
            self.minor_tab = UIImageButton(
                scale(pygame.Rect((1174, 818), (140, 70))),
                "",
                object_id="#minor_tab",
                manager=MANAGER,
            )
            self.tab_showing = self.in_den_tab

            self.in_den_cats = []
            self.out_den_cats = []
            self.minor_cats = []
            self.injured_and_sick_cats = []
            for the_cat in Cat.all_cats_list:
                if (
                    not the_cat.dead
                    and not the_cat.outside
                    and (the_cat.injuries or the_cat.illnesses)
                ):
                    self.injured_and_sick_cats.append(the_cat)
            for cat in self.injured_and_sick_cats:
                if cat.injuries:
                    for injury in cat.injuries:
                        if cat.injuries[injury][
                            "severity"
                        ] != "minor" and injury not in [
                            "pregnant",
                            "recovering from birth",
                            "sprain",
                            "lingering shock",
                        ]:
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif (
                            injury
                            in [
                                "recovering from birth",
                                "sprain",
                                "lingering shock",
                                "pregnant",
                            ]
                            and cat not in self.in_den_cats
                        ):
                            if cat not in self.out_den_cats:
                                self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif cat not in (self.in_den_cats or self.out_den_cats):
                            if cat not in self.minor_cats:
                                self.minor_cats.append(cat)
                if cat.illnesses:
                    for illness in cat.illnesses:
                        if (
                            cat.illnesses[illness]["severity"] != "minor"
                            and illness != "grief stricken"
                        ):
                            if cat not in self.in_den_cats:
                                self.in_den_cats.append(cat)
                            if cat in self.out_den_cats:
                                self.out_den_cats.remove(cat)
                            elif cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        elif illness == "grief stricken":
                            if cat not in self.in_den_cats:
                                if cat not in self.out_den_cats:
                                    self.out_den_cats.append(cat)
                            if cat in self.minor_cats:
                                self.minor_cats.remove(cat)
                            break
                        else:
                            if (
                                cat not in self.in_den_cats
                                and cat not in self.out_den_cats
                                and cat not in self.minor_cats
                            ):
                                self.minor_cats.append(cat)
            self.tab_list = self.in_den_cats
            self.current_page = 1
            self.update_sick_cats()

        self.current_creature = 1

        self.draw_med_den()
        self.update_beast()

    def handle_tab_toggles(self):
        if self.open_tab == "cats":
            self.log_title.hide()
            self.log_box.hide()

            self.hurt_sick_title.show()
            self.last_page.show()
            self.next_page.show()
            self.in_den_tab.show()
            self.out_den_tab.show()
            self.minor_tab.show()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].show()
            for x in range(len(self.cat_names)):
                self.cat_names[x].show()
            for button in self.conditions_hover:
                self.conditions_hover[button].show()
        elif self.open_tab == "log":
            self.hurt_sick_title.hide()
            self.last_page.hide()
            self.next_page.hide()
            self.in_den_tab.hide()
            self.out_den_tab.hide()
            self.minor_tab.hide()
            for cat in self.cat_buttons:
                self.cat_buttons[cat].hide()
            for x in range(len(self.cat_names)):
                self.cat_names[x].hide()
            for button in self.conditions_hover:
                self.conditions_hover[button].hide()

            self.log_title.show()
            self.log_box.show()
    def update_beast(self):

        self.beast_template = {
            "info": "",
            "facts": "",
            "skills_gained": "",
            "species_name": "",
            "main_title": "",
        }
        self.beast1 = self.beast_template
        self.beast2 = self.beast_template

        # get the med cats
        self.beasts = ["crow", "hermit thrush", "rabbit"]

        if not self.beasts:
            all_pages = []
        else:
            all_pages = self.chunks(self.beasts, 1)

        if self.current_creature > len(all_pages):
            if len(all_pages) == 0:
                self.current_creature = 1
            else:
                self.current_creature = len(all_pages)

        if all_pages:
            self.display_med = all_pages[self.current_creature - 1]
        else:
            self.display_med = []

        if len(all_pages) <= 1:
            self.next_creature.disable()
            self.last_creature.disable()
        else:
            if self.current_creature >= len(all_pages):
                self.next_creature.disable()
            else:
                self.next_creature.enable()

            if self.current_creature <= 1:
                self.last_creature.disable()
            else:
                self.last_creature.enable()

        for cat in self.display_med:
            self.beast = UISpriteButton(
                scale(pygame.Rect((870, 330), (300, 300))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
            )
            name = str(self.beast1["main_title"])
            short_name = shorten_text_to_fit(name, 275, 30)
            self.beast_name = pygame_gui.elements.ui_label.UILabel(
                scale(pygame.Rect((1050, 310), (450, 60))),
                short_name,
                object_id=get_text_box_theme("#text_box_30_horizcenter"),
                manager=MANAGER,
            )
            self.beast_info = UITextBoxTweaked(
                "",
                scale(pygame.Rect((1160, 370), (240, 240))),
                object_id=get_text_box_theme("#text_box_22_horizcenter"),
                line_spacing=1,
                manager=MANAGER,
            )
            med_skill = cat.skills.skill_string(short=True)
            med_exp = f"exp: {cat.experience_level}"
            med_working = True
            if cat.not_working():
                med_working = False
            if med_working is True:
                work_status = "This cat can work"
            else:
                work_status = "This cat isn't able to work"
            info_list = [med_skill, med_exp, work_status]
            self.beast_info.set_text("<br>".join(info_list))

    def update_sick_cats(self):
        """
        set tab showing as either self.in_den_cats, self.out_den_cats, or self.minor_cats; whichever one you want to
        display and update
        """
        self.clear_cat_buttons()

        tab_list = self.tab_list

        if not tab_list:
            all_pages = []
        else:
            all_pages = self.chunks(tab_list, 10)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

        # Check for empty list (no cats)
        if all_pages:
            self.display_cats = all_pages[self.current_page - 1]
        else:
            self.display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.next_page.disable()
            self.last_page.disable()
        else:
            if self.current_page >= len(all_pages):
                self.next_page.disable()
            else:
                self.next_page.enable()

            if self.current_page <= 1:
                self.last_page.disable()
            else:
                self.last_page.enable()

        pos_x = 350
        pos_y = 920
        i = 0
        for cat in self.display_cats:
            condition_list = []
            if cat.injuries:
                condition_list.extend(cat.injuries.keys())
            if cat.illnesses:
                condition_list.extend(cat.illnesses.keys())
            if cat.permanent_condition:
                for condition in cat.permanent_condition:
                    if cat.permanent_condition[condition]["moons_until"] == -2:
                        condition_list.extend(cat.permanent_condition.keys())
            conditions = ",<br>".join(condition_list)

            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                cat.sprite,
                cat_object=cat,
                manager=MANAGER,
                tool_tip_text=conditions,
                starting_height=2,
            )

            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 185, 30)
            self.cat_names.append(
                pygame_gui.elements.UITextBox(
                    short_name,
                    scale(pygame.Rect((pos_x - 60, pos_y + 100), (220, -1))),
                    object_id="#text_box_30_horizcenter",
                    manager=MANAGER,
                )
            )

            pos_x += 200
            if pos_x >= 1340:
                pos_x = 350
                pos_y += 160
            i += 1

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
        self.den_base.kill()
        for herb in self.herbs:
            self.herbs[herb].kill()
        self.herbs = {}
        if self.beast_info:
            self.beast_info.kill()
        if self.beast_name:
            self.beast_name.kill()
        self.back_button.kill()
        if game.clan.game_mode != "classic":
            self.help_button.kill()
            self.cat_bg.kill()
            self.last_page.kill()
            self.next_page.kill()
            self.in_den_tab.kill()
            self.out_den_tab.kill()
            self.minor_tab.kill()
            self.clear_cat_buttons()
            self.hurt_sick_title.kill()
            self.cats_tab.kill()
            self.log_tab.kill()
            self.log_title.kill()
            self.log_box.kill()
        if self.beast:
            self.beast.kill()

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
    def __init__(
        self,
        beast_chosen = None,
        common_name = None,
        species_name = None,
        summary = None,
        skills_gained = (),
        facts = None,
        discovered_beasts = (),
        all_beasts = (),
        discovered_status = False):

        print("is this in the right spot")
        self.common_name = common_name
        self.species_name = species_name
        self.summary = summary
        self.skills_gained = skills_gained
        self.facts = facts
        self.discovered_beasts = discovered_beasts
        self.all_beasts = all_beasts
        self.discovered_status = discovered_status

        if self.common_name is None:
            self.assign_beast_info(beast_chosen)
    def assign_beast_info(self, beast_chosen):
        print("beast info function activated")
        if beast_chosen is None:
            print("OH NO THERES NO BEAST CHOSEN. OH NO WHAT INFO DO WE ASSIGN??")
        elif beast_chosen == "crow":
            self.common_name = "crow"
            self.species_name = "corvid xxx"
            self.summary = "crows are very crow-like. blalalla"
            self.skills_gained = ("stuff, " "more stuff, " "and more stuff")
            self.facts = "crows r veveryvery smart"
            self.discovered_status = self.beast_assign_discovery()
            if "crow" not in self.all_beasts:
                self.all_beasts.append(self.common_name)
            else:
                pass
        elif beast_chosen == "rabbit":
            self.common_name = "rabbit"
            self.species_name = "bunny rabbit species"
            self.summary = "bunnies are very bunny like"
            self.skills_gained ("bunny stuff, " "more bunny stuff, " "and more stuff")
            self.facts = "rabbits hop a lot"
            self.discovered_status = self.beast_assign_discovery()
            if "rabbit" not in self.all_beasts:
                self.all_beasts.append(self.common_name)
            else:
                pass
    def beast_assign_discovery(self):

        print("function activated")
        if self.discovered_status:
            self.discovered_beasts.append(self.common_name)
        else:
            pass
        if self.discovered_beasts in self.all_beasts:
            print("discovered beasts in all beasts error check confirmed")
        else:
            print("extra discovered beast has been added. something went wrong")
        if self.all_beasts not in self.discovered_beasts:
            print("this will either signify not all beasts have been discovered OR ... work properly and be that if not discovered,")
            print("then do whatever is in here. eek")
        return self.discovered_status
        

