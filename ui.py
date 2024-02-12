# Imports required libraries
import PySimpleGUI as sg
import json
from functools import partial
import os, sys

# Sets Fixed Values for PySimpleGUI
# TODO - tinker with these settings and see if there is a better way to handle this.
FONT  = ('Meiryo',12)
FONTs = ('Meiryo',8)
par_text = partial(sg.Text, font=FONT)
par_btn = partial(sg.Button, pad=(3,0), font=FONT, enable_events=True, border_width=0)
sg.theme('SystemDefault')
settingsfile = 'settings.json'
languagefile = 'languages/language.json'
# suppress_key_guessing will enforce that keys are set up correctly this is needed as the keys will most likely be pulled from the Language file itself.
sg.set_options(suppress_key_guessing=True,)


class uifunc:
    def __init__(self):
        self.gui_mode = gui_mode.init
        self.detect_mode = detect_mode.init
        self.window = False
        self.plays = 0
        self.load_settings()
        self.ico = self.ico_path('icon.ico')

    # For displaying icons
    # Args: relative_path (str): icon file name
    # Returns: (str): Absolute path of icon file
    # アイコン表示用
    # Args: relative_path (str): アイコンファイル名
    # Returns: (str): アイコンファイルの絶対パス
    def ico_path(self, relative_path:str):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
# Loads settings file and language keys and sets them as objects. sets a return value just in case
# TODO - set up a function that checks if the default language is set to a missing value and start up a first time setup event to pick and set language.
    def load_settings(self):
        setjson = {}
        try:
            with open(settingsfile, 'r') as f:
                setjson = json.load(f)
        finally:
            self.settings = setjson
            return setjson
    # loads the defined langauge from settings and then pulls the dedicated key from language.json
    def load_languagelist(self):
        langlist = {}
        try:
            with open(languagefile, 'r') as l:
                langlist = json.load(l)
        finally:
            self.langlist = langlist
            return langlist
    #sets the UI language objects
    def load_guilanguage(self):
        uilang = {}
        try:
            with open(self.settings['language'], 'r') as sl:
                self.setlanguage = json.load(sl)
                with open(self.langlist[self.setlanguage], 'r') as ul:
                    uilang = json.load(ul)
        finally:
            self.uilanguage = uilang
            return uilang
    #Function for gui_obs_control
    def build_layout_one_scene(self, name, LR=None):

        if LR == None:
            sc = [
                sg.Column([[par_text('Enable')],
                           [sg.Listbox(self.settings[f'obs_enable_{name}'], key=f'obs_enable_{name}', size=(20, 4))],
                           [par_btn('add', key=f'add_enable_{name}'), par_btn('del', key=f'del_enable_{name}')]]),
                sg.Column([[par_text('Disable')],
                           [sg.Listbox(self.settings[f'obs_disable_{name}'], key=f'obs_disable_{name}', size=(20, 4))],
                           [par_btn('add', key=f'add_disable_{name}'), par_btn('del', key=f'del_disable_{name}')]]),
            ]
        else:
            scL = [[
                sg.Column([[par_text('Enable')],
                           [sg.Listbox(self.settings[f'obs_enable_{name}0'], key=f'obs_enable_{name}0', size=(20, 4))],
                           [par_btn('add', key=f'add_enable_{name}0'), par_btn('del', key=f'del_enable_{name}0')]]),
                sg.Column([[par_text('Disable')], [
                    sg.Listbox(self.settings[f'obs_disable_{name}0'], key=f'obs_disable_{name}0', size=(20, 4))],
                           [par_btn('add', key=f'add_disable_{name}0'), par_btn('del', key=f'del_disable_{name}0')]]),
            ]]
            scR = [[
                sg.Column([[par_text('Enable')],
                           [sg.Listbox(self.settings[f'obs_enable_{name}1'], key=f'obs_enable_{name}1', size=(20, 4))],
                           [par_btn('add', key=f'add_enable_{name}1'), par_btn('del', key=f'del_enable_{name}1')]]),
                sg.Column([[par_text('Disable')], [
                    sg.Listbox(self.settings[f'obs_disable_{name}1'], key=f'obs_disable_{name}1', size=(20, 4))],
                           [par_btn('add', key=f'add_disable_{name}1'), par_btn('del', key=f'del_disable_{name}1')]]),
            ]]
            sc = [
                sg.Frame('Scene swap in', scL, title_color='#440000'),
                sg.Frame('Scene swap off', scR, title_color='#440000')
            ]
        ret = [
            [
                par_text('Scene:')
                , par_text(self.settings[f'obs_scene_{name}'], size=(20, 1), key=f'obs_scene_{name}')
                , par_btn('set', key=f'set_scene_{name}')
            ],
            sc
        ]
        return ret


    # Sets the main GUI window.
    def gui_main(self):
        self.gui_mode = gui_mode.main
        self.detect_mode = detect_mode.init
        if self.window:
            self.window.close()
            layout = [
                [sg.Menubar(self.uilanguage['menulist'])],
                [
                    par_text('Plays:'), par_text(str(self.plays), key='txt_plays')
                    ,par_text('Mode:'), par_text(self.detect_mode.name, key='txt_mode')
                    ,par_text(self.uilanguage['obswarning'], key='txt_obswarning', text_color="#ff0000")],
                [par_btn('save', tooltip=self.uilanguage['savefigtt'], key='btn_savefig')],
                [par_text()
                ]
            ]
            if self.settings['dbg_enable_output']:
                layout.append([sg.Output(size=(63, 8), key='output', font=(None, 9))])
            self.window = sg.Window('SDVX helper', layout, grab_anywhere=True,return_keyboard_events=True,resizable=False,finalize=True,enable_close_attempted_event=True,icon=self.ico,location=(self.settings['lx'], self.settings['ly']))
            if self.connect_obs():
                self.window['txt_obswarning'].update('')
    def gui_settings(self):
        self.gui_mode = gui_mode.setting
        if self.window:
            self.window.close()
            layout_obs = [
                [par_text(self.uilanguage['obshost']), sg.Input(self.settings['host'], font=FONT, key='input_host', size=(20,20))],
                [par_text(self.uilanguage['obsport']), sg.Input(self.settings['port'], font=FONT,key='input_port', size=(10,20))],
                [par_text(self.uilanguage['obspass']), sg.Input(self.settings['passwd'], font=FONT, key='input_passwd', size=(20,20), password_char='*')],
            ]
            layout_gamemode = [
                [par_text(self.uilanguage['screenorient']), sg.Radio(self.uilanguage['topright'], group_id='topmode',default=self.settings['top_is_right'], key='top_is_right'), sg.Radio(self.uilanguage['topleft'], group_id='topmode', default=not self.settings['top_is_right'])],
            ]
            layout_etc = [
                [sg.Checkbox(self.uilanguage['saveoncapturechkbox'],self.settings['save_on_capture'], key='save_on_capture', enable_events=True, tooltip=self.uilanguage['saveoncapturett'])],
                [par_text(self.uilanguage['screenshotfolder']), par_btn(self.uilanguage['changebtn'], key='btn_autosave_dir')],
                [sg.Text(self.settings['autosave_dir'], key='txt_autosave_dir')],
                [sg.Checkbox(self.uilanguage['autosavealways'],self.settings['autosave_always'],key='chk_always', enable_events=True)],
                [sg.Checkbox(self.uilanguage['ignorerankd'],self.settings['ignore_rankD'],key='chk_ignore_rankD', enable_events=True)],
                [sg.Button(self.uilanguage['readfromresult'], key='read_from_result')],
                [sg.Button(self.uilanguage['genjacketimgs'], key='gen_jacket_imgs')],
                [sg.Checkbox(self.uilanguage['savejacketimg'], self.settings['save_jacketimg'],key='save_jacketimg')],
                [sg.Text(self.uilanguage['txtpcsetting'], tooltip=self.uilanguage['txtpcsettingtt'])],
                [
                    #par_text(self.uilanguage['obstxtplays']), sg.Input(self.settings['obs_txt_plays'], key='obs_txt_plays', size=(20,1)),
                    sg.Text(self.uilanguage['obstxtplaysheader'],tooltip=self.uilanguage['obstxtplaysheadertt']),sg.Input(self.settings['obs_txt_plays_header'], key='obs_txt_plays_header',size=(10,1)),
                    sg.Text(self.uilanguage['obstxtplaysfooter'],tooltip=self.uilanguage['obstxtplaysheadertt']),sg.Input(self.settings['obs_text_plays_footer'], key='obs_txt_plays_footer', size=(10,1)),
                ],
                [sg.Checkbox(self.uilanguage['alertblastermax'],self.settings['alert_blastermax'],key='alert_blastermax', enable_events=True)],
                [sg.Text(self.uilanguage['logpicbgalpha']), sg.Combo(i for i in range(256),default_value=self.settings['logpic_bg_alpha'],key='logpic_bg_alpha', enable_events=True],
                [sg.Checkbox(self.uilanguage['autoupdate'],self.settings['auto_update'],key='chk_auto_update', enable_events=True)],
                [sg.Text(self.uilanguage['playernametxt']),sg.Input(self.settings['player_name'], key='player_name', size=(30,1))],
            ]
            layout = [
                [sg.Frame(self.uilanguage['layoutobs'], layout=layout_obs,title_color='#000044')],
                [sg.Frame(self.uilanguage['layoutgamemode'], layout=layout_gamemode,title_color='#000044')],
                [sg.Frame(self.uilanguage['layoutetc'],layout=layout_etc,title_color='#000044')],
            ]
            self.window = sg.Window(self.uilanguage['settingswindow'], layout, grab_anywhere=True,return_keyboard_events=True,resizable=False,finalize=True,enable_close_attempted_event=True,icon=self.ico,location=self.settings['lx'],self.settings['ly'])

    def gui_obs_control(self):
         self.gui_mode = gui_mode.obs_control
         if self.window:
             self.window.close()
         obs_scenes = []
         obs_sources = []
         if self.obs != False:
             tmp = self.obs.get_scenes()
             tmp.reverse()
             for s in tmp:
                 obs_scenes.append(s['sceneName'])
         layout_select = self.build_layout_one_scene('Select',0)
         layout_play = self.build_layout_one_scene('play',0)
         layout_result = self.build_layout_one_scene('result',0)
         layout_boot = self.build_layout_one_scene('boot')
         layout_quit = self.build_layout_one_scene('quit')
         layout_obs2 = [
             [par_text(self.uilanguage['scenecollection']),sg.Combo(self.obs.get_scene_collection_list(),key='scene_collection',size=(40,1),enable_events=True)],
             [par_text(self.uilanguage['comboscene']),sg.Combo(obs_scenes, key='combo_scene',size=(40,1),enable_events=True)],
             [par_text]
         ]