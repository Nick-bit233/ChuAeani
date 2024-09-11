def get_arccreate_proj_config_charts_format(chart) -> str:
    lines = [
        f"audioPath: {chart['audioPath']}",
        f"jacketPath: {chart['jacketPath']}",
        f"baseBpm: {chart['baseBpm']}",
        f"bpmText: {chart['bpmText']}",
        f"syncBaseBpm: {chart['syncBaseBpm']}",
        f"title: {chart['title']}",
        f"composer: {chart['composer']}",
        f"charter: {chart['charter']}",
        f"alias: {chart['alias']}",
        f"illustrator: {chart['illustrator']}",
        f"difficulty: {chart['difficulty']}",
        f"difficultyColor: {chart['difficultyColor']}",
        f"lastWorkingTiming: {chart['lastWorkingTiming']}",
        f"previewEnd: {chart['previewEnd']}\n"
    ]
    return f"chartPath: {chart['chartPath']}\n" + '\n'.join(f"  {line}" for line in lines)


def get_arcade_proj_config_format(music_info: dict, c_bpm: float, creator_string: str, alias: str, aff_difficulty_type: int) -> dict:
    template = {
        "Title": f"{music_info['MusicName']}",
        "Artist": f"{music_info['ArtistName']}",
        "BaseBpm": c_bpm,
        "Difficulties": [
            {"Rating": None, "Illustration": None, "ChartDesign": None, "Title": None},
            {"Rating": None, "Illustration": None, "ChartDesign": None, "Title": None},
            {"Rating": f"{music_info['DifficultyName']}" if aff_difficulty_type == 2 else None,
             "Illustration": None,
             "ChartDesign": f"{creator_string} + \n {alias}" if aff_difficulty_type == 2 else None,
             "Title": f"{music_info['MusicName']}" if aff_difficulty_type == 2 else None},
            {"Rating": None, "Illustration": None, "ChartDesign": None, "Title": None}
        ],
        "Difficulties2": {
            str(i): {
                "Rating": None,
                "Illustration": None,
                "ChartDesign": None,
                "Title": None
            } for i in range(4)
        }
    }

    # 仅填写 aff_difficulty_type 对应的项
    template["Difficulties2"][str(aff_difficulty_type)] = {
        "Rating": f"{music_info['DifficultyName']}",
        "Illustration": None,
        "ChartDesign": f"{creator_string} + \n {alias}",
        "Title": f"{music_info['MusicName']}"
    }

    template.update({
        "LastWorkingDifficulty": f"{aff_difficulty_type}",
        "LastWorkingTiming": 0,
        "SkinValues": {
            "Tap": 0,
            "Hold": 0,
            "ArcTap": 0,
            "Track": 0,
            "CriticalLine": 0,
            "Combo": 0,
            "SingleLine": 0
        },
        "ChartDesign": f"{creator_string}",
        "Illustration": None,
        "SkinParticle": 0,
        "SkinParticleArc": 0,
        "SkinDiamond": 0,
        "SkinBackground": "base_light"
    })

    return template
