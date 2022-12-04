import re
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.tabbedpanel import TabbedPanel
from app_lib.pwdgenerator import Password


class Pwdgen(TabbedPanel):
    '''Main kivi app class'''

    # kivy properties gui elements

    settings_info = ObjectProperty()
    status_info = ObjectProperty()
    keyphrase = ObjectProperty()
    password = ObjectProperty()

    set_phraseraw = ObjectProperty()
    set_phraselow = ObjectProperty()
    set_phraseupp = ObjectProperty()

    set_use_uppercase = ObjectProperty()
    set_has_uppercase = ObjectProperty()
    set_use_lowercase = ObjectProperty()
    set_has_lowercase = ObjectProperty()
    set_use_digits = ObjectProperty()
    set_has_digits = ObjectProperty()
    set_use_special = ObjectProperty()
    set_has_special = ObjectProperty()
    set_use_extra = ObjectProperty()
    set_has_extra = ObjectProperty()
    set_extra = ObjectProperty()
    set_except = ObjectProperty()
    set_pwdlen = ObjectProperty()
    set_secretnum = ObjectProperty()
    set_attempts = ObjectProperty()

    set_algorithm = ObjectProperty()

    old_except = ''
    old_extra = ''

    # General
    def get_settings(self):
        """ Return current settings dictionary """

        settings = {}
        settings['keyphrase'] = self.keyphrase.text

        settings['use_uppercase'] = self.set_use_uppercase.active
        settings['has_uppercase'] = self.set_has_uppercase.active

        settings['use_lowercase'] = self.set_use_lowercase.active
        settings['has_lowercase'] = self.set_has_lowercase.active

        settings['use_digits'] = self.set_use_digits.active
        settings['has_digits'] = self.set_has_digits.active

        settings['use_special'] = self.set_use_special.active
        settings['has_special'] = self.set_has_special.active

        settings['use_extra'] = self.set_use_extra.active
        settings['has_extra'] = self.set_has_extra.active

        settings['extra'] = self.set_extra.text
        settings['except'] = self.set_except.text

        settings['pwdlen'] = int(self.set_pwdlen.text)

        settings['secretnum'] = int(self.set_secretnum.text)

        settings['attempts'] = int(self.set_attempts.text)

        settings['algorithm'] = "custom" if self.set_CustomAlgorithm.state == "down" else "MD5"

        return settings

    def clr_password(self):
        """ Clear password string """
        self.password.text = ''

    def get_set_phrase(self):
        """ Return phrase settings for brief current settings info """

        if self.set_phraseraw.state == 'down':
            return 'raw'
        elif self.set_phraselow.state == 'down':
            return 'lowercase'
        elif self.set_phraseupp.state == 'down':
            return 'uppercase'

    def get_box_settings_state(self):
        """
        Set Properties: optional (potential) simbols to use ('set_use') properties
        and oblygatory simbols ('set_has') properties.
        Used in events handling for settings changing: checkboxes optional / obligatory password simbols (has_...) 
        """
        self.set_use = (self.set_use_uppercase, self.set_use_lowercase,
                        self.set_use_digits, self.set_use_special, self.set_use_extra)
        self.set_has = (self.set_has_uppercase, self.set_has_lowercase,
                        self.set_has_digits, self.set_has_special, self.set_has_extra)

    def update_settings_info(self):
        """" Show brief current settings info """

        head = '>>> Current generator settings\n'

        key_phrase = f'Key phrase simbols: {self.get_set_phrase()}\n'

        pwdlen = f'Password length: {self.set_pwdlen.text}\n'

        use = 'Simbols: '
        uselist = []
        if self.set_use_uppercase.active:
            uselist.append('A...Z')
        if self.set_use_lowercase.active:
            uselist.append('a...z')
        if self.set_use_digits.active:
            uselist.append('0...9')
        if self.set_use_special.active:
            uselist.append('#$...')
        if self.set_use_extra.active:
            uselist.append(f'extra: {len(self.set_extra.text)}')
        use += str(uselist) + '\n'

        has = 'Rules: '
        haslist = []
        if self.set_has_uppercase.active:
            haslist.append('A...Z')
        if self.set_has_lowercase.active:
            haslist.append('a...z')
        if self.set_has_digits.active:
            haslist.append('0...9')
        if self.set_has_special.active:
            haslist.append('#$...')
        if self.set_has_extra.active:
            haslist.append(f'extra: {len(self.set_extra.text)}')
        has += str(haslist) + '\n'

        Secret = f'Secret number: {self.set_secretnum.text}' + '\n'

        Algorithm = f'Algorithm: {"custom" if self.set_CustomAlgorithm.state == "down" else "MD5"}'

        self.settings_info.text = head + key_phrase + \
            pwdlen + use + has + Secret + Algorithm

    def update_status(self, current_status='', error=True):
        """" show current status info """
        txt = 'Status: ' + current_status
        self.status_info.text = txt
        if error:
            self.status_info.color = (1, 0, 0, 1)
        else:
            self.status_info.color = (40/255, 130/255, 0/255, 1)

    # GUI events handling
    # Main tab

    def generate_on_release(self):
        """" GENERATE PASSWORD button: try to generate password and refresh status info """

        if self.keyphrase.text == '':
            self.password.text = ''
            self.update_status('no key phrase. Aborted!')
            return

        if int(self.set_pwdlen.text) == 0:
            self.password.text = ''
            self.update_status('zero password lenght. Aborted!')
            return

        if self.set_has_extra.active and self.set_use_extra.active and (len(self.set_extra.text) == 0):
            self.password.text = ''
            self.update_status('no extra simbols set. Aborted!')
            return

        settings = self.get_settings()

        pwd = Password(settings)
        pwd.generate_password()

        if pwd.sucsess:
            self.password.text = pwd.password_value
            self.update_status(
                f'password generated in {str(pwd.attempt_number)} attempts', False)
        else:
            self.update_status(
                f'{pwd.error}. Take {str(pwd.attempt_number)} attempts')

    def toolbuttonclr_on_press(self):
        """ Clr button: clear keyphrase and password """

        self.keyphrase.text = ''
        self.clr_password()

    def showpwd_on_press(self):
        """ Show/hide password button """

        self.password.password = not self.password.password

    def keyphrase_on_text(self, instance, value):
        """ 
        Edit text in keyphrase textinput: remove CRLF, tab. 
        Optional (on settings) convert upper/lower case 
        """

        # replace cr/nl, tab
        value = re.sub("\r\n|\n|\r|\t", ' ', value)
        if self.set_phraseraw.state == 'down':
            instance.text = value
        elif self.set_phraselow.state == 'down':
            instance.text = value.lower()
        elif self.set_phraseupp.state == 'down':
            instance.text = value.upper()

        self.clr_password()

    def exit_on_release(self):
        """ Button exit: stop app """
        App.get_running_app().stop()

    # Settings tab

    def checkbox_use_click(self, instance, value):
        """
        Для всех флагов, определяющих возможность использования тех или иных символов в пароле (use_...), 
        кроме флага Use_extra, установить аналогичное значение парного флага, определяющего обязательность 
        наличия тех или иных символов в наборе (has_...).
        Set flag for obligatory password simbols (has_...) when changing optional password simbols (use_...)
        Для установленного флага Use_extra - сбросить флаг соответствющего реквизита has_extra

        """
        indx = self.set_use.index(instance)

        if value and indx == 4:
            self.set_has[indx].active = False
        else:
            self.set_has[indx].active = value

        self.update_settings_info()

        self.clr_password()

    def checkbox_has_click(self, instance, value):
        """ Set flag for optional password simbols (use_...) when changing obligatory password simbols (has_...) """
        indx = self.set_has.index(instance)
        use = self.set_use[indx].active

        if not use:
            instance.active = False

        self.update_settings_info()

        self.clr_password()

    def set_secretnum_on_text(self, instance, value):
        """ set_secretnum textinput change """
        int_val = 0
        try:
            int_val = int(value)
        except:
            pass
        instance.text = str(int_val)
        self.update_settings_info()

        self.clr_password()

    def set_extra_on_text(self, instance, value):
        """ set_extra textinput change (extra simbols) """

        if instance.text == "":
            self.old_extra = instance.text
            self.clr_password()
            return
        ##not be in set_except
        if re.findall(''.join(['[', instance.text, ']']), self.set_except.text) != []:
            instance.text = self.old_extra

        simbols_set = set(list(instance.text))
        extra = sorted(list(simbols_set))
        instance.text = ''.join(extra)
        self.update_settings_info()

        self.old_extra = instance.text

        self.clr_password()

    def set_except_on_text(self, instance, value):
        """ set_except textinput change (extra simbols) """

        if instance.text == "":
            self.old_except = instance.text
            self.clr_password()
            return
        # not should be present in set_extra
        if re.findall(''.join(['[', instance.text, ']']), self.set_extra.text) != []:
            instance.text = self.old_except

        txt = re.sub('\t', '', instance.text)

        simbols_set = set(list(txt))
        exept = sorted(list(simbols_set))
        instance.text = ''.join(exept)
        self.update_settings_info()

        self.old_except = instance.text

        self.clr_password()

    def algorithm_on_press(self, instance, value):
        """" algorytm settings """
        self.clr_password()
        self.update_settings_info()

# +pwdlen
    def set_pwdlen_on_text(self, instance, value):
        """ set_pwdlen textinput change (extra simbols) """
        if len(instance.text) == 0:
            self.clr_password()
            return

        int_val = 0
        try:
            int_val = int(value)

        except:
            pass

        if int_val == 0:
            int_val = 1

        instance.text = str(int_val)

        self.update_settings_info()
        self.clr_password()

    def set_pwdlen_on_focus(self, instance, focused):
        if not focused:
            self.set_pwdlen_on_enter(instance, instance.text)

    def set_pwdlen_on_enter(self, instance, value):
        if len(value) == 0 or value == '0':
            instance.text = '1'
# -pwdlen

# +attemts

    def set_attempts_on_text(self, instance, value):
        """ set_attempts textinput change (extra simbols) """

        if len(instance.text) == 0:
            self.clr_password()
            return

        int_val = 0
        try:
            int_val = int(value)
        except:
            pass

        if int_val == 0:
            int_val = 1

        instance.text = str(int_val)

        self.clr_password()

    def set_attempts_on_focus(self, instance, focused):
        if not focused:
            self.set_attempts_on_enter(instance, instance.text)

    def set_attempts_on_enter(self, instance, value):
        if len(value) == 0 or value == '0':
            instance.text = '1'
# -attemts
