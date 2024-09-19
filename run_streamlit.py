import traceback

import streamlit as st
from c2s2aff import exec_convert


def main():
    st.title("ChuAeani Beta Version 0.4")

    # Language selection
    language = st.selectbox("Select Language / 选择语言", ["中文", "English"])

    if language == "English":
        labels = {
            "title": "- C2S to AFF Converter -",
            "intro": "For more information, please visit the GitHub Repository:",
            "file_paths": "File and Resources",
            "file": "Choose a .c2s file",
            "music_info_file": "Choose a Music.xml File",
            "ogg_file": "Choose the corresponding .ogg file (optional)",
            "jpg_file": "Choose the corresponding .jpg file (optional)",
            "aff_project_dir": "Output Aff Project Directory Path",
            "music_info": "Beatmap & Music Information",
            "music_name": "Music Name",
            "artist_name": "Artist Name",
            "difficulty_type": "Difficulty Type (usually, 0,1,2,3 for Past, Present, Future and Beyond)",
            "difficulty_name": "Difficulty Name (e.g. Master, you can also use Custom)",
            "aff_project_name": "Aff Project Name (leave blank will use the same as Music Name)",
            "conversion_settings": "Conversion Settings",
            "audio_offset": "Audio Offset (ms)",
            "aff_project_style": "Aff Project Style ('Single' for only output .aff file)",
            "check_note_overlapping": "Check Note Overlapping",
            "add_air_note_deco": "Add arrow shape Trace for translated :green[AIR] Notes",
            "experiment_tap": "Convert Long Tap/ExTap to Experimental ArcTap",
            "byd_arctap": "Allow AIR to be converted to Beyond range ArcTap",

            "slide_style_head": ":blue-background[Slide] Notes translation style",
            "slide_style_options": [":violet[Dual-color Arcs] (Red-Blue Arcs overlap, to ignore hand order)",
                                    "Single-color Arcs: :blue[Blue]", "Single-color Arcs: :red[Red]",
                                    "Single-color Arcs: :green[Green]"],

            "slide_position_head": ":blue-background[Slide] Notes translation style",
            "slide_position_options": ["Ground", "Sky-input (FTR range)", "Sky-input (BYD range)"],

            "flick_style_head": ":blue[Flick] Notes translation style",
            "flick_style_options": ["As Tap Notes", "Short Dual-color Arcs", "Short Blue Arcs",
                                    "Short Red Arcs", "Short Green Arcs"],

            "air_style_head": ":green[AIR] Notes translation style",
            "air_style_options": ["As Sky ArcTaps", "Up Dual-color Arcs", "Up Blue Arcs",
                                  "Up Red Arcs", "Up Green Arcs"],

            "air_hold_style_head": ":green-background[AIR-Hold] translation style",
            "air_hold_style_options": ["None", "Traces", "Dual-color Arcs", "Blue Arcs",
                                       "Red Arcs", "Green Arcs"],

            "air_action_style_head": ":violet[AIR-Action] translation style",
            "air_action_style_options": ["None", "Traces", "Dual-color Arcs", "Blue Arcs",
                                         "Red Arcs", "Green Arcs"],

            "air_action_warning": "Warning: Translate AIR-Action Notes to Arcs may cause "
                                  "Arcs go beyond the limit!",
            "style_conflict_warning": "Warning: Translate Slide Notes to Sky-input may cause "
                                      "position conflict with other Notes!",
            "other_settings": "Other Settings (Working on it ...)",
            "convert": "Convert",
            "no_file": "Please upload a .c2s file!",
            "success": "Conversion Completed!"
        }
    else:
        labels = {
            "title": "- C2S 转 AFF 转换器 -",
            "intro": "源码仓库和使用说明详见：",
            "file_paths": "输入待转换文件",
            "file": "选择一个 .c2s 文件",
            "music_info_file": "选择一个对应的 Music.xml 文件",
            "ogg_file": "选择音频 .ogg 文件（可选）",
            "jpg_file": "选择曲绘 .jpg 文件（可选）",
            "aff_project_dir": "Aff 项目输出路径",
            "music_info": "Arc 谱面信息",
            "music_name": "曲名",
            "artist_name": "曲师",
            "difficulty_type": "难度类型（通常为0,1,2,3，即 Past, Present, Future 和 Beyond）",
            "difficulty_name": "难度名称（可与上文对应，也可自定义）",
            "aff_project_name": "Aff项目名称（不填写则默认曲名）",
            "conversion_settings": "转换设置",
            "audio_offset": "音频偏移（ms）",
            "aff_project_style": "Aff 项目格式（'Single' 则仅输出 .aff 文件）",
            "check_note_overlapping": "检查音符重叠",
            "add_air_note_deco": "为转换的 :green[AIR] 音符添加箭头状黑线",
            "experiment_tap": "变长Tap/ExTap转换为实验性ArcTap",
            "byd_arctap": "允许将Air转换到Beyond范围的天键",

            "slide_style_head": ":blue-background[Slide] 音符样式转换选项:",
            "slide_style_options": [":violet[双色音弧]（红蓝蛇叠加，以忽视手序）", "单色音弧：:blue[蓝]",
                                    "单色音弧：:red[红]", "单色音弧：:green[绿]"],
            "slide_position_head": ":blue-background[Slide] 音符的垂直位置转换选项:",
            "slide_position_options": ["地面", "Future范围天空", "Beyond范围天空"],

            "flick_style_head": ":blue[Flick] 音符样式转换选项:",
            "flick_style_options": ["视为Tap音符", "碎:violet[双色音弧]", "碎单色音弧：:blue[蓝]",
                                    "碎单色音弧：:red[红]", "碎单色音弧：:green[绿]"],

            "air_style_head": ":green[AIR] 音符样式转换选项:",
            "air_style_options": ["转换为天键", "向上:violet[双色音弧]", "向上单色音弧：:blue[蓝]",
                                  "向上单色音弧：:red[红]", "向上单色音弧：:green[绿]"],

            "air_hold_style_head": ":green-background[AIR-Hold] 音符转换选项:",
            "air_hold_style_options": ["不转换", "转换为黑线", "天空:violet[双色音弧]", "天空单色音弧：:blue[蓝]",
                                       "天空单色音弧：:red[红]", "天空单色音弧：:green[绿]"],

            "air_action_style_head": ":violet[AIR-Action] 音符转换选项:",
            "air_action_style_options": ["不转换", "转换为黑线", ":violet[双色音弧]", "单色音弧：:blue[蓝]",
                                         "单色音弧：:red[红]", "单色音弧：:green[绿]"],
            "air_action_warning": "注意：选择将 AIR-Action 转换为音弧可能导致超界！",
            "style_conflict_warning": "注意：选择将 Slide 转换到天空线上可能导致与其他天空音符重叠！",
            "other_settings": "其他设置（部分选项正在施工中……）",
            "convert": "转换",
            "no_file": "请至少上传一个 .c2s 文件！",
            "success": "转换完成！"
        }

    st.title(labels["title"])

    st.markdown(labels["intro"] + "[GitHub Repository](https://github.com/Nick-bit233/ChuAeani)")

    st.header(labels["file_paths"])
    file = st.file_uploader(labels["file"], type="c2s")

    music_info_file = st.file_uploader(labels["music_info_file"], type="xml")

    ogg_file = st.file_uploader(labels["ogg_file"], type="ogg")

    jpg_file = st.file_uploader(labels["jpg_file"], type="jpg")

    # aff_project_dir_path = st.text_input(labels["aff_project_dir"], "")

    st.header(labels["music_info"])
    if language == "English":
        st.markdown("""
        **Instructions:** \n
        If no Music.xml File is uploaded, you may need to fill in the following settings manually. \n
        Otherwise, if your do not want an Arcade/ArcCreate Project(only .aff),you can also leave these settings as default. \n 
        """)
    else:
        st.markdown("""
        **说明:** \n
        如果你上传了Music.xml文件，你可以无需填写下面这些设置，系统将自动识别。\n
        否则，请手动填写，这些信息将填入Arcaea工程的相关信息中。如果你只需要输出.aff文件，也可以忽略它们。
        """)
    music_name = st.text_input(labels["music_name"], "")
    artist_name = st.text_input(labels["artist_name"], "")
    difficulty_type = st.selectbox(labels["difficulty_type"], [0, 1, 2, 3, 4])
    difficulty_name = st.text_input(labels["difficulty_name"], "Master")
    aff_project_name = st.text_input(labels["aff_project_name"], "")

    st.header(labels["conversion_settings"])
    audio_offset = st.number_input(labels["audio_offset"], min_value=-100000, max_value=100000, value=0)
    aff_project_style = st.selectbox(labels["aff_project_style"], ["Arcade", "ArcCreate", "Single"])

    st.header(labels["other_settings"])
    slide_style = st.radio(labels["slide_style_head"], labels["slide_style_options"], index=0, horizontal=True)
    slide_pos_y = st.radio(labels["slide_position_head"], labels["slide_position_options"], index=0, horizontal=True)
    if labels['slide_position_options'].index(slide_pos_y) > 0:
        st.warning(labels["style_conflict_warning"])

    flick_style = st.radio(labels["flick_style_head"], labels["flick_style_options"], index=1, horizontal=True)
    air_style = st.radio(labels["air_style_head"], labels["air_style_options"], index=0, horizontal=True)
    air_hold_style = st.radio(labels["air_hold_style_head"], labels["air_hold_style_options"], index=1, horizontal=True)
    air_action_style = st.radio(labels["air_action_style_head"], labels["air_action_style_options"],
                                index=2, horizontal=True)
    if labels['air_action_style_options'].index(air_action_style) == 2:
        st.warning(labels["air_action_warning"])
    experiment_tap = st.checkbox(labels["experiment_tap"], False, disabled=True)
    byd_arctap = st.checkbox(labels["byd_arctap"], False, disabled=True)
    add_air_note_deco = st.checkbox(labels["add_air_note_deco"], True, disabled=False)
    check_note_overlapping = st.checkbox(labels["check_note_overlapping"], False, disabled=True)

    if st.button(labels["convert"]):
        if not file:
            st.error(labels["no_file"])
            return
        configs = {
            "File": file,
            "MusicInfoFile": music_info_file,
            "OggFile": ogg_file,
            "JpgFile": jpg_file,
            "AudioOffset": audio_offset,
            "MusicName": music_name,
            "ArtistName": artist_name,
            "DifficultyType": difficulty_type,
            "DifficultyName": difficulty_name,
            "AffProjectName": aff_project_name,
            "AffProjectStyle": aff_project_style,
            "ConvertConfigs": {
                "check_note_overlapping": check_note_overlapping,
                "add_air_note_deco": add_air_note_deco,
                "experiment_tap": experiment_tap,
                "slide_style": labels['slide_style_options'].index(slide_style),
                "slide_pos_y": labels['slide_position_options'].index(slide_pos_y),
                "flick_style": labels['flick_style_options'].index(flick_style),
                "air_style": labels['air_style_options'].index(air_style),
                "air_hold_style": labels['air_hold_style_options'].index(air_hold_style),
                "air_action_style": labels['air_action_style_options'].index(air_action_style)
            }
        }

        # Check if MusicInfoFilePath is provided, and if so, set defaults
        if music_info_file:
            configs["MusicName"] = ""
            configs["ArtistName"] = ""
            configs["DifficultyName"] = ""
            configs["AffProjectName"] = ""

        try:
            zip_path, proj_name = exec_convert(configs)
            st.success("Conversion Completed!" if language == "English" else "转换完成！")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Download Converted Files" if language == "English" else "下载文件",
                    data=f,
                    file_name=f"{proj_name}.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"Error: {e}")
            st.error(traceback.format_exc())


if __name__ == "__main__":
    main()
