import configparser
import os

class Settings:
    def __init__(self, file_name="config.ini"):
        self.file_name = file_name
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        """
        Loads configuration from the file.
        If the file doesn't exist, or if it's missing sections or options,
        it populates them with default values and saves the file.
        It also handles migrating settings from the installer.
        """
        self.config.read(self.file_name)

        # One-time migration from installer config
        needs_saving = False
        if self.config.has_section('transcription'):
            print("Performing one-time migration of installer settings...")
            engine = self.config.get('transcription', 'engine', fallback='local_whisper')
            # The installer uses 'local_whisper' or 'openai', app uses 'local' or 'openai'
            engine_type = 'local' if engine == 'local_whisper' else 'openai'
            
            if not self.config.has_section('General'):
                self.config.add_section('General')
            self.config.set('General', 'engine_type', engine_type)

            if self.config.has_option('transcription', 'openai_api_key'):
                api_key = self.config.get('transcription', 'openai_api_key', fallback='')
                if not self.config.has_section('OpenAI'):
                    self.config.add_section('OpenAI')
                self.config.set('OpenAI', 'api_key', api_key)
            
            self.config.remove_section('transcription')
            needs_saving = True

        defaults = {
            'General': {
                'engine_type': 'local',
                'hotkey_mode': 'hold',
                'hotkey': 'ctrl+space',
                'device': 'cpu',
                'first_run_complete': 'false'
            },
            'Local': {
                'model_size': 'tiny.en'
            },
            'OpenAI': {
                'api_key': ''
            }
        }
        
        for section, options in defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                needs_saving = True
            for option, value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, value)
                    needs_saving = True
                    
        if needs_saving:
            self.save()

    def save(self):
        with open(self.file_name, 'w') as configfile:
            self.config.write(configfile)

    def get(self, section, option, fallback=None):
        return self.config.get(section, option, fallback=fallback)

    def get_general(self, option):
        return self.get('General', option)

    def get_local(self, option):
        return self.get('Local', option)
        
    def get_openai(self, option):
        return self.get('OpenAI', option)

    def set(self, section, option, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, option, str(value))
        self.save() 