#!/usr/bin/env python3
# -*- coding: ascii -*-
import pygame
import textwrap

from ..game_structure.windows import SaveAsImage

from scripts.utility import scale
from .Screens import Screens
from scripts.utility import get_text_box_theme, scale_dimentions, generate_sprite, shorten_text_to_fit
from scripts.cat.cats import Cat
import pygame_gui
from scripts.game_structure.ui_elements import UIImageButton
from scripts.game_structure.game_essentials import game, MANAGER


class CodeInspectScreen(Screens):
    cat_life_stages = ["newborn", "kitten", "adolescent", "adult", "senior"]
    
    def __init__(self, name=None):
        self.back_button = None
        self.previous_cat_button = None
        self.previous_cat = None
        self.next_cat_button = None
        self.next_cat = None
        self.the_cat = None
        self.cat_image = None
        self.cat_elements = {}
        self.checkboxes = {}
        self.scars_shown = None
        self.acc_shown_text = None
        self.override_not_working_text = None
        self.sprite_elements = {}
        self.tortie_toggle = True
        self.tortie_button_scroll = {}
        self.info_column_size = ()


        
        #Image Settings: 
        self.code_info_shown = True
        self.displayed_lifestage = None
        self.scars_shown = True
        self.acc_shown = True
        self.override_not_working = False

        # Dev Mode Things
        self.code_info_shown_text = None
        
        super().__init__(name)
    
    def handle_event(self, event):
        # Don't handle the events if a window is open.     
        if game.switches['window_open']:
            return
        
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.cat_setup()
                    self.get_sprite_number()
                    if self.tortie_toggle:
                        self.update_column_text()
                    else:
                        pass
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.cat_setup()
                    self.get_sprite_number()
                    if self.tortie_toggle:
                        self.update_column_text()
                    else:
                        pass
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_life_stage:
                self.displayed_life_stage = min(self.displayed_life_stage + 1, 
                                                len(self.valid_life_stages) - 1)
                self.get_sprite_number()
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.previous_life_stage:
                self.displayed_life_stage = max(self.displayed_life_stage - 1, 
                                                0)
                self.get_sprite_number()
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.tortie_info_button:
                self.update_column_text()
            elif event.ui_element == self.checkboxes["code_info_shown"]:
                if self.code_info_shown:
                    self.code_info_shown = False
                    self.change_screen('sprite inspect screen')
                else:
                    self.code_info_shown = True

                
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["scars_shown"]:
                if self.scars_shown:
                    self.scars_shown = False
                else:
                    self.scars_shown = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["acc_shown"]:
                if self.acc_shown:
                    self.acc_shown = False
                else:
                    self.acc_shown = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["override_not_working"]:
                if self.override_not_working:
                    self.override_not_working = False
                    self.get_sprite_number()
                else:
                    self.override_not_working = True
                    self.get_sprite_number()
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.cat_elements["favourite_button"]:
                self.the_cat.favourite = False
                self.cat_elements["favourite_button"].hide()
                self.cat_elements["not_favourite_button"].show()
            elif event.ui_element == self.cat_elements["not_favourite_button"]:
                self.the_cat.favourite = True
                self.cat_elements["favourite_button"].show()
                self.cat_elements["not_favourite_button"].hide()
    
        return super().handle_event(event)
    


    def screen_switches(self):  
       
        self.code_info_shown = True      
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button"
                                             , manager=MANAGER)
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button"
                                                 , manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.sprite_box = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((100, 250), (700, 900))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/relationship_details_frame.png").convert_alpha(),
                                                                (800, 700))
                                                            )
        self.info_box = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((800, 200), (700, 1000))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/mediator_selected_frame.png").convert_alpha(),
                                                                (800, 700))
                                                            )
        self.previous_life_stage = UIImageButton(scale(pygame.Rect((180, 1000), (76, 100))), "", object_id="#arrow_right_fancy",
                                                 starting_height=2)
        
        self.next_life_stage = UIImageButton(scale(pygame.Rect((680, 1000), (76, 100))), "", object_id="#arrow_left_fancy",
                                             starting_height=2)
       
        

        self.tortie_button_scroll[
            "info_scroll_container"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((850, 250), (700, 950))), manager=MANAGER)

        scroll_pos = None
        if "info_scroll_container" in self.tortie_button_scroll and \
                            self.tortie_button_scroll["info_scroll_container"].vert_scroll_bar:
                        scroll_pos = self.tortie_button_scroll["info_scroll_container"].vert_scroll_bar.start_percentage
        if scroll_pos is not None:
                        self.tortie_button_scroll["info_scroll_container"].vert_scroll_bar.set_scroll_from_start_percentage(
                            scroll_pos)

       
        self.tortie_button_scroll[
            "info_scroll_container"].set_scrollable_area_dimensions(
            (700, 0))
        self.tortie_button_scroll[
            "info_scroll_container"].horiz_scroll_bar.hide()
        
        self.tortie_info_button =  pygame_gui.elements.UIButton(scale(pygame.Rect((250, 65), (360, 60))), "(Click here for more info)", container=self.tortie_button_scroll["info_scroll_container"],object_id="#invis_button", 
                                             starting_height=2,manager=MANAGER)
        # Toggle Text:
        self.scars_shown_text = pygame_gui.elements.UITextBox("Show Scar(s)", scale(pygame.Rect((550, 1160), (290, 100))),
                                                              object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        self.acc_shown_text = pygame_gui.elements.UITextBox("Show Accessory", scale(pygame.Rect((173, 1160), (290, 100))),
                                                            object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                            starting_height=2)
        self.override_not_working_text = pygame_gui.elements.UITextBox("Show as Healthy", scale(pygame.Rect((180, 1260), (290, 100))),
                                                                 object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        self.code_info_shown_text = pygame_gui.elements.UITextBox("Show Code Info", scale(pygame.Rect((574, 1260), (290, 100))),
                                                                 object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        self.cat_setup()
        self.get_sprite_number()
        self.update_column_text()
        return super().screen_switches()

    def get_tortie_info(self):
        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        tortie_info_string = ""
        tortie_info_title = ""
        
        
        if self.the_cat.pelt.name not in ['Tortie', 'Calico']:
            return ""
        tortie_info_title += "<b>TORTIE INFO --</b>" + "\n"
        tortie_info_string += "Pelt Base Type: " + str(self.the_cat.pelt.tortiebase) + "\n"
        tortie_info_string += "Pelt Base Color: " + str(self.the_cat.pelt.colour) + "\n"
        tortie_count = len(self.the_cat.pelt.pattern)
        if tortie_count == 1:
            tortie_info_string += "Tortie Patch: " + ', '.join(self.the_cat.pelt.pattern) + "\n"
        elif tortie_count > 1:
            tortie_info_string += "Tortie Patches: " + ', '.join(self.the_cat.pelt.pattern) + "\n"
        tortie_info_string += "Tortie Patch Type: " + str(self.the_cat.pelt.tortiepattern) + "\n"
        tortie_info_string += "Tortie Patch Color: " + str(self.the_cat.pelt.tortiecolour) + "\n"
        tortie_info_string = textwrap.indent(tortie_info_string, '   ')
        tortie_info_string = tortie_info_title + tortie_info_string
        return tortie_info_string

    def generate_tortie_column_info(self):
        """generates the thing this screen was made for--to show code info not stated in profile screen"""
        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        output = ""

        # PELT + BASICS
        output +="<b>Basic pelt info!</b>"+ "\n"
        output += "Pelt Type: " + str(self.the_cat.pelt.name)
        output += "\n"
        if self.the_cat.pelt.name not in ['Tortie', 'Calico']:
            output += "Pelt Color: " + str(self.the_cat.pelt.colour) + "\n"
        output += self.get_tortie_info()
        if self.the_cat.pelt.vitiligo:
            output += "Vitiligo: " + str(self.the_cat.pelt.vitiligo)
        else:
            output += "Vitiligo: None"
        output += "\n"
        if self.the_cat.pelt.white_patches:
            output += "White Patch: "+ (self.the_cat.pelt.white_patches) # this may seem unnecessary, but if you just make it str by using str(), it keeps in the brackets for some reason?
        else:
            output += "White Patches: None"
        if self.the_cat.pelt.points:
            output += "\n" + "Colorpoints: " + str(self.the_cat.pelt.points)
        if not self.the_cat.pelt.eye_colour2:
                output += "\n" + "Eye Color: " + str(self.the_cat.pelt.eye_colour) + "\n"
        elif self.the_cat.pelt.eye_colour2:
            output += "\n" + "Eye Colors: "+ str(self.the_cat.pelt.eye_colour) + "and" + str(self.the_cat.pelt.eye_colour2) + "\n"
        output += "Skin: " + str(self.the_cat.pelt.skin) + "\n"


        # TINTS, ACC, SCARS
        output += "\n" + "<b>Extra info! (such as tints, scars, etc)</b>"+ "\n"
        output += "White Patches Tint: " + str(self.the_cat.pelt.white_patches_tint) + "\n"
        output += "Accessory: " + str(self.the_cat.pelt.accessory) + "\n"
        if self.the_cat.pelt.scars:
            scar_count = len(self.the_cat.pelt.scars)
            if scar_count == 1:
                output += "Scar: " + ', '.join(self.the_cat.pelt.scars) + "\n"
            elif scar_count > 1:
                output += "Scars: " + ', '.join(self.the_cat.pelt.scars) + "\n"
        else:
            output += "Scars: None" + "\n"
        if self.the_cat.pelt.reverse:
            output += "Reversed: True" + "\n"
        else:
            output += "Reversed: False" + "\n"


        # FACETS + FADED STATUS IN THE FUTURE
        output += "\n" + "<b>Miscellanous things you cannot view in game!</b>"+ "\n"
        output += "Trait Facets: " + str(self.the_cat.personality.get_facet_string())
       
        return output
    def generate_column_info(self):
        """generates the thing this screen was made for--to show code info not stated in profile screen"""
        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        output = ""

        # PELT + BASICS
        output +="<b>Basic pelt info!</b>"+ "\n"
        output += "Pelt Type: " + str(self.the_cat.pelt.name)
        output += "\n"
        if self.the_cat.pelt.name not in ['Tortie', 'Calico']:
            output += "Pelt Color: " + str(self.the_cat.pelt.colour) + "\n"
        if self.tortie_toggle:
            output += self.get_tortie_info()
        else:
            pass
        if self.the_cat.pelt.vitiligo:
            output += "Vitiligo: " + str(self.the_cat.pelt.vitiligo)
        else:
            output += "Vitiligo: None"
        output += "\n"
        if self.the_cat.pelt.white_patches:
            output += "White Patch: " + (self.the_cat.pelt.white_patches) # this may seem unnecessary, but if you just make it str by using str(), it keeps in the brackets for some reason?
        else:
            output += "White Patches: None"
        if self.the_cat.pelt.points:
            output += "\n" + "Colorpoints: " + str(self.the_cat.pelt.points)
        if not self.the_cat.pelt.eye_colour2:
                output += "\n" + "Eye Color: " + str(self.the_cat.pelt.eye_colour) + "\n"
        elif self.the_cat.pelt.eye_colour2:
            output += "\n" + "Eye Colors: "+ str(self.the_cat.pelt.eye_colour) + " and " + str(self.the_cat.pelt.eye_colour2) + "\n"
        output += "Skin: " + str(self.the_cat.pelt.skin) + "\n"


        # TINTS, ACC, SCARS
        output += "\n" + "<b>Extra info! (such as tints, scars, etc)</b>"+ "\n"
        output += "White Patches Tint: " + str(self.the_cat.pelt.white_patches_tint) + "\n"
        output += "Accessory: " + str(self.the_cat.pelt.accessory) + "\n"
        if self.the_cat.pelt.scars:
            scar_count = len(self.the_cat.pelt.scars)
            if scar_count == 1:
                output += "Scar: " + ', '.join(self.the_cat.pelt.scars) + "\n"
            elif scar_count > 1:
                output += "Scars: " + ', '.join(self.the_cat.pelt.scars) + "\n"
        else:
            output += "Scars: None" + "\n"
        if self.the_cat.pelt.reverse:
            output += "Reversed: True" + "\n"
        else:
            output += "Reversed: False" + "\n"


        # FACETS + FADED STATUS IN THE FUTURE
        output += "\n" + "<b>Miscellanous things you cannot view in game!</b>"+ "\n"
        output += "Trait Facets: " + str(self.the_cat.personality.get_facet_string())
        
        return output

    def update_column_text(self):
        if self.tortie_toggle:
            if self.the_cat.pelt.name not in ["Tortie", "Calico"]:
                self.tortie_info_button.hide()
                self.cat_elements["info_column"].hide()
                self.cat_elements["info_column"] = pygame_gui.elements.UITextBox(self.generate_column_info(),
                                                                        scale(pygame.Rect((0, 0), (600, -1))),
                                                                        container=self.tortie_button_scroll["info_scroll_container"],
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_30_horizleft"),
                                                                            )
                self.info_column_size = self.cat_elements["info_column"].get_relative_rect()
                self.tortie_button_scroll[
                    "info_scroll_container"].set_scrollable_area_dimensions(
                    (700, self.info_column_size.height))
            else:
                self.cat_elements["info_column"].show()
                self.tortie_toggle = False
                self.cat_elements["info_column"].hide()
                self.tortie_info_button.hide()
                self.cat_elements["info_column"] = pygame_gui.elements.UITextBox(self.generate_column_info(),
                                                                        scale(pygame.Rect((0, 0), (600, -1))),
                                                                        container=self.tortie_button_scroll["info_scroll_container"],
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_30_horizleft"),
                                                                            )
                self.tortie_info_button = pygame_gui.elements.UIButton(scale(pygame.Rect((250, 65), (360, 60))), "(Click here for more info)", container=self.tortie_button_scroll["info_scroll_container"],object_id="#invis_button", 
                                                starting_height=2,manager=MANAGER)
                self.info_column_size = self.cat_elements["info_column"].get_relative_rect()
                self.tortie_button_scroll[
                    "info_scroll_container"].set_scrollable_area_dimensions(
                    (700, self.info_column_size.height))
                self.cat_elements["info_column"].show()
                self.tortie_info_button.show()
        else:
            if self.the_cat.pelt.name not in ["Tortie", "Calico"]:
                self.tortie_info_button.hide()
                self.cat_elements["info_column"].hide()
                self.cat_elements["info_column"] = pygame_gui.elements.UITextBox(self.generate_column_info(),
                                                                        scale(pygame.Rect((0, 0), (600, -1))),
                                                                        container=self.tortie_button_scroll["info_scroll_container"],
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_30_horizleft"),
                                                                            )
                self.info_column_size = self.cat_elements["info_column"].get_relative_rect()
                self.tortie_button_scroll[
                    "info_scroll_container"].set_scrollable_area_dimensions(
                    (700, self.info_column_size.height))
            else:
                self.tortie_toggle = True
                self.cat_elements["info_column"].hide()
                self.tortie_info_button.hide()
                self.cat_elements["info_column"] = pygame_gui.elements.UITextBox(self.generate_tortie_column_info(),
                                                                        scale(pygame.Rect((0, 0), (600, -1))),
                                                                        container=self.tortie_button_scroll["info_scroll_container"],
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_30_horizleft"),
                                                                            )
                self.tortie_info_button = pygame_gui.elements.UIButton(scale(pygame.Rect((250, 65), (360, 60))), "(Click again to close)", container=self.tortie_button_scroll["info_scroll_container"],object_id="#invis_button", 
                                                starting_height=2,manager=MANAGER)
                self.info_column_size = self.cat_elements["info_column"].get_relative_rect()
                self.tortie_button_scroll[
                    "info_scroll_container"].set_scrollable_area_dimensions(
                    (700, self.info_column_size.height))
                self.cat_elements["info_column"].show()
                self.tortie_info_button.show()
    


    def get_sprite_number(self):
        sprite_number = 0
        for ele in self.sprite_elements:
            self.sprite_elements[ele].kill()
        self.sprite_elements = {}
        if self.displayed_life_stage == 0:
            sprite_number = 20
        elif self.the_cat.not_working() and self.displayed_life_stage in [1, 2] and not self.override_not_working:
            sprite_number = 19
        elif self.the_cat.not_working() and self.displayed_life_stage in [3, 4] and not self.override_not_working:
            sprite_number = 18 
        elif self.the_cat.pelt.paralyzed and self.displayed_life_stage == 1:
            sprite_number = str(17) + " (previously " + str(self.the_cat.pelt.cat_sprites['kitten']) + ")"
        elif self.the_cat.pelt.paralyzed and self.displayed_life_stage == 2:
            sprite_number = str(17) + " (previously " + str(self.the_cat.pelt.cat_sprites['adolescent']) + ")"
        elif self.the_cat.pelt.paralyzed and self.displayed_life_stage == 3:
            sprite_number = str(self.the_cat.pelt.cat_sprites['para_adult']) + " (previously " + str(self.the_cat.pelt.cat_sprites['adult']) + ")"
        elif self.the_cat.pelt.paralyzed and self.displayed_life_stage == 4:
            sprite_number = str(self.the_cat.pelt.cat_sprites['para_adult']) + " (previously " + str(self.the_cat.pelt.cat_sprites['senior']) + ")"
        elif self.displayed_life_stage == 1:
            sprite_number = self.the_cat.pelt.cat_sprites['kitten']
        elif self.displayed_life_stage == 2:
            sprite_number = self.the_cat.pelt.cat_sprites['adolescent']
        elif self.displayed_life_stage == 3:
            sprite_number = self.the_cat.pelt.cat_sprites['adult']
        elif self.displayed_life_stage == 4:
            sprite_number = self.the_cat.pelt.cat_sprites['senior']

        self.sprite_elements["sprite_number_string"] = pygame_gui.elements.UITextBox("Sprite " + str(sprite_number),
                                                                      scale(pygame.Rect(
                                                                        (218, 1006),
                                                                        (500, 80))),
                                                                       object_id=get_text_box_theme(
                                                                        "#text_box_40_horizcenter"), manager=MANAGER)


    def cat_setup(self): 
        """Sets up all the elements related to the cat """
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}
        
        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        
        # Gather list of current and previous life states
        # "young adult", "adult", and "senior adult" all look the same: collapse to adult
        # This is not the best way to do it, so if we make them have difference appearances, this will
        # need to be changed/removed. 
        if self.the_cat.age in ["young adult", "adult", "senior adult"]:
            current_life_stage = "adult"
        else:
            current_life_stage = self.the_cat.age
            
        self.valid_life_stages = []
        if game.settings["dev_mode"]:
            for life_stage in CodeInspectScreen.cat_life_stages:
                self.valid_life_stages.append(life_stage)
                if life_stage == current_life_stage:
                    self.future_life_stages = len(self.cat_life_stages) - len(self.valid_life_stages)
        else:
            for life_stage in CodeInspectScreen.cat_life_stages:
                self.valid_life_stages.append(life_stage)
                if life_stage == current_life_stage:
                    self.future_life_stages = len(self.cat_life_stages) - len(self.valid_life_stages)
                    break
        
        #Store the index of the currently displayed life stage.
        if game.settings["dev_mode"]:
            self.displayed_life_stage = len(self.valid_life_stages) - self.future_life_stages - 1
        else:
            self.displayed_life_stage = len(self.valid_life_stages) - 1
        
        #Reset all the toggles
        self.lifestage = None
        self.scars_shown = True
        self.acc_shown = True
        self.override_not_working = False
        
        # Make the cat image
        self.make_cat_image()
        if self.the_cat.pelt.name in ['Tortie', 'Calico']:
            self.tortie_info_button.show()
        else: 
            self.tortie_info_button.hide()
        
        cat_name = str(self.the_cat.name)  # name
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        short_name = shorten_text_to_fit(cat_name, 800, 40)
        
        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(short_name,
                                                                          scale(pygame.Rect((50, 120), (-1, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_40_horizcenter"), manager=MANAGER)
        name_text_size = self.cat_elements["cat_name"].get_relative_rect()

        self.cat_elements["cat_name"].kill()

        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(short_name,
                                                                      scale(pygame.Rect(
                                                                        (480 - name_text_size.width, 265),
                                                                        (name_text_size.width * 2, 80))),
                                                                       object_id=get_text_box_theme(
                                                                        "#text_box_40_horizcenter"), manager=MANAGER)
        self.cat_elements["info_column"] = pygame_gui.elements.UITextBox(self.generate_column_info(),
                                                                     scale(pygame.Rect((0, 0), (700, -1))),
                                                                     container=self.tortie_button_scroll["info_scroll_container"],
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_30_horizleft"),
                                                                        )
        self.info_column_size = self.cat_elements["info_column"].get_relative_rect()
        self.tortie_button_scroll[
            "info_scroll_container"].set_scrollable_area_dimensions(
            (700, self.info_column_size.height))
        # Fullscreen
        if game.settings['fullscreen']:
            x_pos = 420 - name_text_size.width//2
        else:
            x_pos = 425 - name_text_size.width
        self.cat_elements["favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                ((x_pos, 275), (56, 56))),
                                                              "",
                                                              object_id="#fav_cat",
                                                              manager=MANAGER,
                                                              tool_tip_text='Remove favorite status',
                                                              starting_height=2)

        self.cat_elements["not_favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                    ((x_pos, 275),
                                                                        (56, 56))),
                                                                 "",
                                                                 object_id="#not_fav_cat",
                                                                 manager=MANAGER,
                                                                 tool_tip_text='Mark as favorite',
                                                                 starting_height=2)  
        if self.the_cat.favourite:
            self.cat_elements["favourite_button"].show()
            self.cat_elements["not_favourite_button"].hide()
        else:
            self.cat_elements["favourite_button"].hide()
            self.cat_elements["not_favourite_button"].show()
        # Write the checkboxes. The text is set up in switch_screens.  
        self.update_checkboxes()
        
        
        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()
    
    def update_checkboxes(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        # "Show Scars"
        self.make_one_checkbox((500, 1150), "scars_shown", self.scars_shown, self.the_cat.pelt.scars)
        
        # "Show accessories"
        self.make_one_checkbox((100, 1150), "acc_shown", self.acc_shown, self.the_cat.pelt.accessory)
        
        # "Show as healthy"
        self.make_one_checkbox((100, 1250), "override_not_working", self.override_not_working, self.the_cat.not_working(),
                               disabled_object_id="#checked_checkbox")
        # "Show code info"
        self.make_one_checkbox((500, 1250), "code_info_shown", self.code_info_shown,
                               disabled_object_id="#checked_checkbox")
        
    def make_one_checkbox(self, location:tuple, name:str, stored_bool: bool, cat_value_to_allow=True,
                          disabled_object_id = "#unchecked_checkbox"):
        """Makes a single checkbox. So I don't have to copy and paste this 5 times. 
            if cat_value_to_allow evaluates to False, then the unchecked checkbox is always used the the checkbox 
            is disabled"""
        
        if not cat_value_to_allow:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = disabled_object_id,
                                                            starting_height=4)
            self.checkboxes[name].disable()
        elif stored_bool:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = "#checked_checkbox",
                                                            starting_height=4)
        else:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = "#unchecked_checkbox",
                                                            starting_height=4)
    
    def make_cat_image(self):
        """Makes the cat image """
        if "cat_image" in self.cat_elements:
            self.cat_elements["cat_image"].kill()
        
        self.cat_image = generate_sprite(self.the_cat, life_state=self.valid_life_stages[self.displayed_life_stage], 
                                         scars_hidden=not self.scars_shown,
                                         acc_hidden=not self.acc_shown, always_living=False, 
                                         no_not_working=self.override_not_working)
        
        self.cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((110, 310),(700, 700))),
            pygame.transform.scale(self.cat_image, scale_dimentions((700, 700)))
        )
      
    def determine_previous_and_next_cat(self):
        """'Determines where the next and previous buttons point too."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and self.the_cat.df == game.clan.instructor.df and \
                not (self.the_cat.outside or self.the_cat.exiled):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat
    
    def exit_screen(self):
        self.back_button.kill()
        self.back_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.previous_life_stage.kill()
        self.previous_life_stage = None
        self.tortie_button_scroll["info_scroll_container"].kill()
        self.tortie_button_scroll["info_scroll_container"] = None
        self.tortie_info_button.kill()
        self.tortie_info_button = None
        self.next_life_stage.kill()
        self.next_life_stage = None
        self.sprite_box.kill()
        self.sprite_box = None
        self.info_box.kill()
        self.info_box = None
        self.code_info_shown_text.kill()
        self.code_info_shown_text = None
        self.scars_shown_text.kill()
        self.scars_shown = None
        self.acc_shown_text.kill()
        self.acc_shown_text = None
        self.override_not_working_text.kill()
        self.override_not_working_text = None
        
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        for ele in self.sprite_elements:
            self.sprite_elements[ele].kill()
        self.sprite_elements = {}
        return super().exit_screen()
    
    def update_disabled_buttons(self):
        # Previous and next cat button
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()
            
        if self.displayed_life_stage >= len(self.valid_life_stages) - 1:
            self.next_life_stage.disable()
        else:
            self.next_life_stage.enable()
            
        if self.displayed_life_stage <= 0:
            self.previous_life_stage.disable()
        else:
            self.previous_life_stage.enable()
        