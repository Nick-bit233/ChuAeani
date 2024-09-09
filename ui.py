import dearpygui.dearpygui as dpg


class ConverterUI:
    def __init__(self, exec_convert_func):
        self.exec_convert_func = exec_convert_func
        self.create_ui()

    def create_ui(self):
        with ((dpg.window(label="Converter", width=800, height=800))):
            # File Path
            self.file_path = self.add_row("Beatmap File (.c2s) Path:", is_path=True, file_extension=".c2s")

            # Music Info File Path
            self.music_info_path = self.add_row("Music File (.xml) Path:", is_path=True, file_extension=".xml")

            # Aff Project Dir Path
            self.aff_project_dir = self.add_row("Generated Project Directory Path:", is_path=True, folder=True)

            dpg.add_text("If an Music.xml File is set, you can leave these settings as default.\n"
                         "Otherwise, fill these manually.", show=True, )

            # Audio Offset
            self.audio_offset = self.add_row("Audio Offset:", default_value="0", indent=40)

            # Music Name
            self.music_name = self.add_row("Music Name:", indent=40)

            # Artist Name
            self.artist_name = self.add_row("Artist Name:", indent=40)

            # Difficulty Type
            self.difficulty_type = self.add_row("Difficulty Type:", default_value="2", indent=40)

            # Difficulty Name
            self.difficulty_name = self.add_row("Difficulty Name:", default_value="Master", indent=40)

            # Aff Project Name
            self.aff_project_name = self.add_row("Generated Project Name:", indent=40)

            dpg.add_text("Generated Project Style:")

            # Aff Project Style
            self.aff_project_style = dpg.add_radio_button(items=["ArcCreate", "Arcade", "Single"],
                                                          indent=40, default_value="ArcCreate")

            dpg.add_text("Extra Control Settings (Experimental).")

            # Check Note Overlapping
            self.check_note_overlapping = dpg.add_checkbox(label="Check Note Overlapping", indent=40)

            dpg.add_text(" ")

            # Run Button
            dpg.add_button(label="Run Conversion", callback=self.run_conversion, indent=80, width=140, height=60)

    def add_row(self, label_text, indent=0, default_value="", is_path=False, folder=False, file_extension=".*"):
        with dpg.group(horizontal=True, indent=indent):
            dpg.add_text(label_text, show=True)
            text_input = dpg.add_input_text(width=400, default_value=default_value)
            if is_path:
                dpg.add_button(label="Select Folder" if folder else "Select File",
                               callback=lambda: self.select_path(text_input, folder, file_extension))
        return text_input

    def select_path(self, text_input, folder, extension):
        with dpg.file_dialog(width=600, height=600, label="Select Folder" if folder else "Select File",
                             directory_selector=folder, show=True, callback=lambda s, a: self.set_path(text_input, a)):
            dpg.add_file_extension(extension)

    def set_path(self, text_input, selection):
        dpg.set_value(text_input, selection['file_path_name'])

    def run_conversion(self):
        configs = {
            "FilePath": dpg.get_value(self.file_path),
            "MusicInfoFilePath": dpg.get_value(self.music_info_path),
            "AudioOffset": int(dpg.get_value(self.audio_offset)),
            "MusicName": dpg.get_value(self.music_name),
            "ArtistName": dpg.get_value(self.artist_name),
            "DifficultyType": int(dpg.get_value(self.difficulty_type)),
            "DifficultyName": dpg.get_value(self.difficulty_name),
            "AffProjectDirPath": dpg.get_value(self.aff_project_dir),
            "AffProjectStyle": dpg.get_value(self.aff_project_style),
            "AffProjectName": dpg.get_value(self.aff_project_name),
            "ConvertConfigs": {
                "check_note_overlapping": dpg.get_value(self.check_note_overlapping)
            }
        }
        self.exec_convert_func(configs)
        dpg.add_text("Conversion Successful!", parent=dpg.last_item())


def start_ui(exec_convert_func):
    dpg.create_context()

    # Optionally, you can load a custom font
    # with dpg.font_registry():
    #     default_font = dpg.add_font("path_to_your_font_file.ttf", 20)
    #     dpg.bind_font(default_font)

    ConverterUI(exec_convert_func)
    dpg.create_viewport(title='AirARChuni Ver0.1', width=800, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
