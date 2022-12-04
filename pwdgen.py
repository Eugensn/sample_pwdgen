from kivy.app import App
from app_lib.kivy_app import Pwdgen


class PwdgenApp(App):
    def build(self):
        pwdgen = Pwdgen()

        pwdgen.get_box_settings_state()
        pwdgen.update_settings_info()

        return pwdgen

    def on_stop(self):
        self.root_window.close()


if __name__ == '__main__':
    PwdgenApp().run()
