from typing import List

from arcfutil import aff
from arcfutil.aff import Arc, Tap, Hold

### arcfutil usage
# a_normal_list = [
#     aff.Timing(0, 222.22),
#     aff.Tap(0, 1),
#     aff.Hold(0, 100, 2),
#     aff.Arc(0, 200, 0, 1, 's', 1, 0, 0, True, [0, 100, 200]),
#     aff.TimingGroup(
#         aff.Timing(0, 222.22),
#     )
# ]
#
# afflist = aff.AffList(a_normal_list)
# aff.dumps(afflist, '0.aff')

Chuni_OffsetResolution = 384
Aff_AudioOffset = -667
C_NOTE_TYPES = ['TAP', 'CHR', 'FLK',
                'HLD',
                'SXC', 'SXD', 'SLC', 'SLD',
                'AIR', 'AUL', 'AUR',
                'ASC', 'ASD', 'AHD',
                'ADL', 'ADR', 'ADW']
# configs
check_note_overlapping = False  # check if after converting tap notes overlapping in the same lane.


# class AffNote:
#     def __init__(self, start_time, end_time, type, props):
#         self.time = (start_time, end_time)
#         self.type = type  # tap/hold/arc/arctap/timing
#         self.props = props
#
#     def to_string(self):
#         # TODO: format the output string as .aff file.
#         return f"{self.time}\t{self.type}\t{self.props}"


def read_c2s_file(file_path):
    def convert_to_number(value):
        """尝试将字符串转换为整数或浮点数"""
        try:
            # 尝试转换为整数
            return int(value)
        except ValueError:
            try:
                # 如果失败，则尝试转换为浮点数
                return float(value)
            except ValueError:
                # 如果都失败，则返回原始值（可能是字符串）
                return value

    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().strip().split('\n\n')  # 按空行分割内容

    # 第一部分：版本等信息
    first_part = data[0].strip().split('\n')
    metadata = {}
    for line in first_part:
        key, *values = line.split('\t')
        metadata[key] = [convert_to_number(v) for v in values]  # 转换值

    # 第二部分：BPM、拍号、速度变化等信息
    second_part = data[1].strip().split('\n')
    timing_list = []
    for line in second_part:
        elements = line.split('\t')
        timing_list.append([convert_to_number(e) for e in elements])  # 转换值

    # 第三部分：每个音符的详细信息
    third_part = data[2].strip().split('\n')
    notes_list = []
    for line in third_part:
        elements = line.split('\t')
        notes_list.append([convert_to_number(e) for e in elements])  # 转换值

    return metadata, timing_list, notes_list


def find_note_lane_overlap_partition(a, b):
    # 16 areas to 4k
    partitions = [(0, 4), (4, 8), (8, 12), (12, 16)]

    best_partition_index = -1
    max_overlap_length = 0

    # try count evey partition to find the longest overlapping.
    for index, (start, end) in enumerate(partitions):
        overlap_start = max(a, start)
        overlap_end = min(b, end)

        if overlap_start < overlap_end:
            overlap_length = overlap_end - overlap_start

            if overlap_length > max_overlap_length:
                max_overlap_length = overlap_length
                best_partition_index = index

    return best_partition_index + 1


def convert_time_beats_to_ms(c_note, bpm, audio_beats=4, audio_note_time=4, aff_audio_offset=0):
    measure = c_note[1]  # The measure number usually in the second position
    offset = c_note[2]  # The offset usually in the third position

    # Calculate the duration of each beat in milliseconds
    beat_duration_ms = 60000 / bpm

    # Calculate the start time of the measure in milliseconds
    measure_start_time_ms = (measure - 1) * (audio_beats * beat_duration_ms)

    # Calculate the time corresponding to the offset in milliseconds
    offset_time_ms = (offset / Chuni_OffsetResolution) * (audio_beats * beat_duration_ms)

    # Calculate the absolute time for the note
    start_time_ms = measure_start_time_ms + offset_time_ms + aff_audio_offset

    # Initialize end time to start time by default
    end_time_ms = start_time_ms

    duration = 0
    # For SFL timing line, duration specified at index 3
    if c_note[0] == 'SFL' and isinstance(c_note[3], int):
        duration = c_note[3]
    # For ASC ASD and ALD, duration specified at index 7
    elif c_note[0] in ['ASC', 'ASD', 'ALD'] and len(c_note) > 7 and isinstance(c_note[7], int):
        duration = c_note[7]
    elif c_note[0] in ['AHX'] and len(c_note) > 6 and isinstance(c_note[6], int):
        duration = c_note[6]
    # Other types notes, duration specified at index 5
    elif len(c_note) > 5 and isinstance(c_note[5], int):
        duration = c_note[5]  # Get the duration from c_note

    # Calculate end offset time in milliseconds
    end_offset = (duration / Chuni_OffsetResolution) * (audio_beats * beat_duration_ms)
    end_time_ms += end_offset  # Calculate end time

    return int(start_time_ms), int(end_time_ms)  # Return as a tuple of (start_time, end_time)er


def find_note_lane_midpoint_partition(a, b):
    # 定义分区的范围
    partitions = [(0, 4), (4, 8), (8, 12), (12, 16)]

    # 计算中点
    midpoint = (a + b) / 2

    # 检查中点是否在分区内
    for index, (start, end) in enumerate(partitions):
        if start <= a <= end and start <= b <= end:
            return index + 1, True

    proportion = mapping_midpoint(midpoint, ground=True)

    return proportion, False


def mapping_midpoint(midpoint, ground=True):
    if ground:
        # 如果不在任何分区，计算比例
        if midpoint < 0:
            return -0.5
        elif midpoint > 16:
            return 1.5
        else:
            # 将中点从[0, 16]映射到[0, 1]
            proportion = midpoint / 16
            # 然后将其缩放到[-0.5, 1.5]
            proportion = proportion * (1.5 + 0.5) - 0.5
            return proportion
    else:
        return midpoint / 16


def mapping_y_axis(c_value, c_ground=1.0, a_ground=0.0, c_sky=5.0, a_sky=1.0):
    m = (a_sky - a_ground) / (c_sky - c_ground)
    b = a_ground - m * c_ground
    if c_value > c_sky:
        return 0.67 * (m * c_value + b)
    else:
        return m * c_value + b


# def convert_note_type(note_type, start_time, end_time, note) -> list[Arc | Tap | Hold]:
#     target_notes = []
#     if note_type in ['TAP', 'CHR', 'FLK']:
#         # TAP, CHR, FLK to Arcaea Tap
#         note_lane_left = note[3]  # The left start of chuni note
#         note_lane_width = note[4]  # The width of chuni note
#
#         if len(note) > 5 and note[5] == "UP":
#             a_note_x = mapping_midpoint(note_lane_left + note_lane_width / 2, ground=False)
#             target_notes.append(
#                 aff.Arc(start_time, start_time + 3, a_note_x, a_note_x, 's', 1, 1, 0, True, [start_time]))
#         else:
#             # Mapping the note lane to Arcaea lane
#
#             # BASIC RULE: The Chuni note lane is from 0 to 16, and the width of the note is 1.
#             # if a note is equal or inside zone (0, 4), (4, 8), (8, 12) or (12, 16),
#             # it is mapping to the 0, 1, 2, 3 lane in Arcaea.
#
#             # OVERLAPPING FUNC:
#             # if a note cross more than one zones, it is mapping to the lane that has the longest overlapping.
#             # a_lane = find_note_lane_overlap_partition(note_lane_left, note_lane_left + note_lane_width)
#             # target_notes.append(aff.Tap(start_time, a_lane))
#
#             # MIDPOINT FUNC (default):
#             # if a note cross more than one zones, it is mapping to an ArcTap note which the co-trace arc starts in the
#             # (midpoint/16, 0) and with duration 3ms.
#             a_lane, is_ground = find_note_lane_midpoint_partition(note_lane_left, note_lane_left + note_lane_width)
#             if is_ground:
#                 target_notes.append(aff.Tap(start_time, a_lane))
#             else:
#                 target_notes.append(
#                     aff.Arc(start_time, start_time + 3, a_lane, a_lane, 's',
#                             0, 0, 0, True, [start_time]))
#
#             # DYNAMIC ARC NOTE FUNC (TODO: experiment)
#             # use arcaea experimental ArcTap that can shift note width to corresponding to chuni note width.
#
#     if note_type in ['HLD', 'HXD']:
#         if start_time == end_time:
#             return target_notes
#         # HLD to Arcaea Hold
#         note_lane_left = note[3]  # The left start of chuni note
#         note_lane_width = note[4]  # The width of chuni note
#         # Mapping the note lane to Arcaea lane
#         a_lane = find_note_lane_overlap_partition(note_lane_left, note_lane_left + note_lane_width)
#         target_notes.append(aff.Hold(start_time, end_time, a_lane))
#
#         if len(note) > 6 and note[6] == "UP":
#             a_note_x = mapping_midpoint(note_lane_left + note_lane_width / 2, ground=False)
#             target_notes.append(
#                 aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
#                         1, 1, 0, True, [end_time]))
#
#     if note_type in ['SXC', 'SXD', 'SLC', 'SLD']:
#         if start_time == end_time:
#             return target_notes
#         # SXC, SXD, SLC, SLD to Arcaea Arc
#         arc_start_x = mapping_midpoint(note[3] + note[4] / 2, ground=True)
#         arc_end_x = mapping_midpoint(note[6] + note[7] / 2, ground=True)
#         arc_y_defalut = 0
#         s_easing = 'si' if note_type in ['SXC', 'SLC'] else 's'
#
#         target_notes.append(
#             aff.Arc(start_time, end_time, arc_start_x, arc_end_x, s_easing,
#                     arc_y_defalut, arc_y_defalut, 0, False, []))
#     if note_type in ['AIR', 'AUL', 'AUR', 'ADL', 'ADR', 'ADW']:
#         # AIR, AUL, AUR to Arcaea ArcTap
#         # usually only marks an air over. so ignoring it just now.
#         pass
#     if note_type in ['ASC', 'ASD', 'AHD', 'AHX', 'ALD']:
#         # ASC ASD AHD AHX: 中二的air hold 绿线，
#         # 其中AHD AHX定义直线，ASC ASD定义曲线，可定义由哪一个note引导上升，绿线默认在y=5.0位置（arc y=1.0位置）
#         # ALD：用作表演性质的air线，其x、y轴起始点位置、颜色等均可指定，翻译为完整的arc黑线
#         # 中二的air线没有宽度，x轴的位置定为常规note的中点 ，即note[3] + note[4] / 2
#         # ASC, ASD, AHD, ALD to Arcaea Arc Trace。
#         arc_start_x = mapping_midpoint(note[3] + note[4] / 2, ground=True)
#         if note_type in ['AHD', 'AHX']:
#             arc_end_x = arc_start_x
#         else:
#             arc_end_x = mapping_midpoint(note[8] + note[9] / 2, ground=True)
#
#         arc_y_defalut = 1.0
#         arc_y_start, arc_y_end = arc_y_defalut, arc_y_defalut
#         if note_type == 'ALD':
#             arc_y_start = mapping_y_axis(note[6])
#             arc_y_end = mapping_y_axis(note[10])
#             if len(note) > 11:
#                 arc_color = note[11]
#
#         s_easing = 'si' if note_type in ['ASC'] else 's'
#
#         target_notes.append(
#             aff.Arc(start_time, end_time, arc_start_x, arc_end_x, s_easing,
#                     arc_y_start, arc_y_end, 0, True, []))
#
#         # If a note has Suffix "UP", ADD a sky note at the tail.
#         if len(note) > 5 and note[0] == "AHX" and note[5] == "TAP":
#             a_note_x = mapping_midpoint(note[3] + note[4] / 2, ground=False)
#             target_notes.append(
#                 aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
#                         1, 1, 0, True, [end_time]))
#
#     return target_notes


def get_chuni_air_arrow(start_time, note_x, direction='up'):
    arrow_traces = [
        aff.Arc(start_time, start_time, note_x - 0.2, note_x, 's',
                0.50, 0.80, 0, True, []),
        aff.Arc(start_time, start_time, note_x + 0.2, note_x, 's',
                0.50, 0.80, 0, True, []),
        aff.Arc(start_time, start_time, note_x - 0.2, note_x - 0.2, 's',
                0.00, 0.50, 0, True, []),
        aff.Arc(start_time, start_time, note_x + 0.2, note_x + 0.2, 's',
                0.00, 0.50, 0, True, []),
        aff.Arc(start_time, start_time, note_x - 0.2, note_x, 's',
                0.00, 0.30, 0, True, []),
        aff.Arc(start_time, start_time, note_x + 0.2, note_x, 's',
                0.00, 0.30, 0, True, []),
    ]
    return arrow_traces


def restrict_y_axis(arc_y):
    if arc_y < 0:
        return 0
    if arc_y > 1.5:
        return 1.5
    return arc_y


def convert_notes_by_group(group, bpm) -> list[aff.Note]:
    # group: {"type": "Single", "sky_end": False, "list": [head_note]}
    # group: {"type": "Single", "sky_end": True, "list": [head_note, tail_note]}
    # group: {"type": "Hold", "sky_end": True, "list": [head_note, tail_note]}
    # group: {"type": "Snake", "sky_end": False, "list": [head_note, ...]}
    # group: {"type": "Trace", "sky_end": False, "list": [head_note]}
    target_notes = []
    last_arc_color = 0
    if group["type"] == "Single":
        head_note = group["list"][0]
        start_time, end_time = convert_time_beats_to_ms(head_note, bpm, aff_audio_offset=Aff_AudioOffset)
        note_lane_left, note_lane_width = head_note[3], head_note[4]
        # TODO: check FLK as other builds.
        if group["sky_end"]:  # build as ArcTap
            a_note_x = mapping_midpoint(note_lane_left + note_lane_width / 2, ground=False)
            target_notes.append(
                aff.Arc(start_time, start_time + 3, a_note_x, a_note_x, 's',
                        1, 1, 0, True, [start_time]))
            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(start_time, a_note_x))

        else:
            a_lane, is_inside_lane = find_note_lane_midpoint_partition(note_lane_left, note_lane_left + note_lane_width)
            if is_inside_lane:
                target_notes.append(aff.Tap(start_time, a_lane))
            else:
                target_notes.append(
                    aff.Arc(start_time, start_time + 3, a_lane, a_lane, 's',
                            0, 0, 0, True, [start_time]))

    elif group["type"] == "Hold":
        head_note = group["list"][0]
        start_time, end_time = convert_time_beats_to_ms(head_note, bpm, aff_audio_offset=Aff_AudioOffset)

        note_lane_left, note_lane_width = head_note[3], head_note[4]

        a_lane = find_note_lane_overlap_partition(note_lane_left, note_lane_left + note_lane_width)
        target_notes.append(aff.Hold(start_time, end_time, a_lane))

        if group["sky_end"]:  # Add an ArcTap at the end of the hold.
            tail_note = group["list"][1]

            a_note_x = mapping_midpoint(tail_note[3] + tail_note[4] / 2, ground=False)
            target_notes.append(
                aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
                        1, 1, 0, True, [end_time]))
            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(end_time, a_note_x))

    elif group["type"] == "Snake":
        # TODO: Combine continues slide notes to a single Arc.
        for note in group["list"]:

            note_type = note[0]
            start_time, end_time = convert_time_beats_to_ms(note, bpm, aff_audio_offset=Aff_AudioOffset)
            if note_type in ['SXC', 'SXD', 'SLC', 'SLD']:
                if start_time == end_time:
                    return target_notes
                # SXC, SXD, SLC, SLD to Arcaea Arc
                # TODO：config slide default y
                arc_y_defalut = 0
                arc_x_start = mapping_midpoint(note[3] + note[4] / 2, ground=True)
                arc_x_end = mapping_midpoint(note[6] + note[7] / 2, ground=True)
                s_easing = 'si' if note_type in ['SXC', 'SLC'] else 's'

                target_notes.append(
                    aff.Arc(start_time, end_time, arc_x_start, arc_x_end, s_easing,
                            arc_y_defalut, arc_y_defalut, 0, False, []))
            else:  # End with an AIR
                tail_note = note
                a_note_x = mapping_midpoint(tail_note[3] + tail_note[4] / 2, ground=False)
                target_notes.append(
                    aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
                            1, 1, 0, True, [end_time]))
                # Add chuni air style trace decorations.
                target_notes.extend(get_chuni_air_arrow(end_time, a_note_x))

    elif group["type"] == "Trace":
        note = group["list"][0]
        note_type = note[0]
        start_time, end_time = convert_time_beats_to_ms(note, bpm, aff_audio_offset=Aff_AudioOffset)

        arc_x_start = mapping_midpoint(note[3] + note[4] / 2, ground=True)
        if note_type in ['AHD', 'AHX']:  # 无平移trace
            arc_x_end = arc_x_start
        else:  # 有平移trace
            arc_x_end = mapping_midpoint(note[8] + note[9] / 2, ground=True)

        arc_y_defalut = 1.0  # 非ALD的，永远在 y=1 位置
        arc_y_start, arc_y_end = arc_y_defalut, arc_y_defalut
        if note_type in ['ALD', 'ASD']:
            arc_y_start = mapping_y_axis(note[6])
            arc_y_end = mapping_y_axis(note[10])
            if len(note) > 11:
                arc_color = note[11]

        s_easing = 'si' if note_type in ['ASC'] else 's'  # 仅ASC转换为曲线

        target_notes.append(
            aff.Arc(start_time, end_time, arc_x_start, arc_x_end, s_easing,
                    arc_y_start, arc_y_end, 0, True, []))
        # 对于 AHD ASD AHX，默认转译结尾一个长度为1/8拍的红蛇，作为air-action，TODO：提供选项改为天键
        air_action_time = 60000 / bpm / 8

        if note_type in ['AHD', 'ASD', 'AHX']:
            target_notes.append(
                aff.Arc(end_time, end_time + air_action_time, arc_x_end, arc_x_end, 's',
                        restrict_y_axis(arc_y_end), restrict_y_axis(arc_y_end), 1, False, []))
        # 对于ALD，检查持续时间和第五个值是否为间隔时间t
        if note_type == 'ALD':
            if len(note) > 7 and isinstance(note[5], int) and note[5] > 0:
                t = note[5]
                duration = note[7]
                if t < duration:
                    # 每隔 t offset 添加一个air-action
                    for i in range(t, duration, t):
                        # 时间插值
                        audio_beats = 4  # TODO： parametric this.
                        beat_duration_ms = 60000 / bpm
                        t_start = (start_time +
                                   (i / Chuni_OffsetResolution) * (audio_beats * beat_duration_ms))
                        # 位置插值  TODO：考虑红蛇的位移也进行插值
                        t_x = arc_x_start + (arc_x_end - arc_x_start) * i / duration
                        t_y = restrict_y_axis(arc_y_start + (arc_y_end - arc_y_start) * i / duration)
                        target_notes.append(
                            aff.Arc(t_start, t_start + air_action_time, t_x, t_x, 's',
                                    t_y, t_y, 1, False, []))
                else:
                    # 在结尾添加一个 air-action
                    t_y = restrict_y_axis(arc_y_end)
                    target_notes.append(
                        aff.Arc(end_time, end_time + air_action_time, arc_x_end, arc_x_end, 's',
                                t_y, t_y, 1, False, []))
                    if arc_y_start != arc_y_end:
                        # TODO: 添加重叠的 air-action 黑线效果
                        pass
                        # target_notes.append(get_chuni_y_air_actions(arc_x_start, arc_x_end, arc_y_start, arc_y_end))

        # 对于紧接着地面音符的air线，添加黑线提示，默认情况下不添加天键。TODO：提供选项可添加天键
        if len(note) > 5 and note[5] in ['TAP', 'CHR', 'FLK', 'HLD', 'HXD', 'SLD']:
            # Add ArcTap note
            # target_notes.append(
            #     aff.Arc(start_time, start_time + 3, arc_start_x, arc_start_x, 's',
            #             1, 1, 0, True, [start_time]))

            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(start_time, arc_x_start))
    return target_notes


def convert_to_aff(timing_list, notes_list) -> aff.AffList:
    c_bpm = 100

    # 1. Set BPM and Convert SFL timing_list to AffNote objects
    a_timing_notes = []
    sfl_end_time = 0
    for c_timing in timing_list:
        if c_timing[0] == 'BPM':
            c_bpm = float(c_timing[3])
            a_timing_notes.append(aff.Timing(0, c_bpm))
        if c_timing[0] == 'SFL':
            start_time, sfl_end_time = convert_time_beats_to_ms(c_timing, c_bpm, aff_audio_offset=Aff_AudioOffset)
            a_timing_notes.append(aff.Timing(start_time, c_bpm * float(c_timing[4])))
    if sfl_end_time > 0:
        # reset to the original BPM
        a_timing_notes.append(aff.Timing(sfl_end_time, c_bpm))

    # 2. Convert notes_list to Aff note objects
    a_notes = []
    if len(a_timing_notes) <= 0:
        a_notes.append(aff.Timing(0, c_bpm))

    # Pair the chuni notes to groups, in convenience to convert to arcaea notes.
    a_note_groups = []

    processed_indices = set()
    for i in range(len(notes_list)):
        if i in processed_indices:
            continue
        head_note = notes_list[i]
        head_note_type = head_note[0]
        group = {
            "type": "Single",  # single / hold / snake / trace
            "sky_end": False,
            "list": [head_note]
        }
        if head_note_type in ['TAP', 'CHR', 'FLK'] and i + 1 < len(notes_list):
            # search for next notes
            next_note = notes_list[i + 1]
            next_note_target = next_note[5] if len(next_note) > 5 else None
            if next_note[0] in ['AIR', 'AUL', 'AUR'] and next_note_target == head_note_type:
                group["sky_end"] = True
                group["list"].append(next_note)
                processed_indices.add(i + 1)
        elif head_note_type in ['HLD', 'HXD'] and i + 1 < len(notes_list):
            # Search for any AIR note which appeared in end of the Hold note.
            # As there may be multiple Hold-AIR notes at different lanes, note position check is required.
            head_note_position = (head_note[3], head_note[4])
            group["type"] = "Hold"
            for j in range(i + 1, len(notes_list)):
                next_note = notes_list[j]
                next_note_target = next_note[5] if len(next_note) > 5 else None
                next_note_position = (next_note[3], next_note[4])
                if next_note[0] in ['AIR', 'AUL', 'AUR'] and next_note_target == head_note_type \
                        and next_note_position == head_note_position:
                    group["sky_end"] = True
                    group["list"].append(next_note)
                    processed_indices.add(j)
                    break
        elif head_note_type in ['SXC', 'SXD', 'SLC', 'SLD']:
            group["type"] = "Snake"
            curr_tail = (head_note[6], head_note[7])

            # Search for continued slide notes. SLC to SLC, end with SLD, SXC to SXC, end with SXD
            for j in range(i + 1, len(notes_list)):
                next_slide = notes_list[j]
                next_slide_type = next_slide[0]
                next_slide_head = (next_slide[3], next_slide[4])

                if next_slide_type == head_note_type and next_slide_head == curr_tail:
                    group["list"].append(next_slide)
                    curr_tail = (next_slide[6], next_slide[7])
                    processed_indices.add(j)
                elif (next_slide_type == 'SLD' and head_note_type == 'SLC') \
                        or (next_slide_type == 'SXD' and head_note_type == 'SXC') \
                        and next_slide_head == curr_tail:
                    group["list"].append(next_slide)
                    curr_tail = (next_slide[6], next_slide[7])
                    processed_indices.add(j)
                    # 再检查slide尾部紧跟着的下一个note是否是air
                    if j + 1 < len(notes_list):
                        end_note = notes_list[j + 1]
                        end_note_target = end_note[5] if len(end_note) > 5 else None
                        end_note_position = (end_note[3], end_note[4])
                        if end_note[0] in ['AIR', 'AUL', 'AUR'] and end_note_target == next_slide_type \
                                and end_note_position == curr_tail:
                            group["sky_end"] = True
                            group["list"].append(end_note)
                            processed_indices.add(j + 1)
                    break
                if head_note_type in ['SXD', 'SLD'] and next_slide_type in ['AIR', 'AUL', 'AUR'] \
                        and next_slide_head == curr_tail:
                    group["sky_end"] = True
                    group["list"].append(next_slide)
                    processed_indices.add(j)
                    break
        elif head_note_type in ['ASC']:
            group["type"] = "Trace"
            # 可以像slide一样做合并处理，不过由于默认是黑线，有无合并视觉上看起来都相似，先跳过
            # TODO：如果后面要做选项air hold翻译为蛇，则需要ASC做合并处理，并标记为sky snake
        elif head_note_type in ['ASD', 'ALD', 'AHD', 'AHX']:
            # ASD AHD AHX 都在结尾有1个默认的air-action，不清楚是否有其他标记可以解除该设定
            # 如果要某处同时出现多个air-action，则需要用ALD替换ASD/AHD/AHX，ASC可以结尾接ALD
            # ASC 因为总是接着后续的ASC或ASD/ALD，因此不需要对ASC处理结尾
            # ALD 格式解析:
            # ALD	104	0	1	6	1	5.0	       4     1	6	 1.0	  DEF
            # ALD  [起始时间] [起点x] [t] [起点y] [持续时间] [终点x]  [终点y] [类型标注]
            # t = 每隔offest t 放置一个air-action，持续时间不足t的，至少有一个。 t=0的话则不生成air-action
            # 猜想：ALD在同一时间，生成y轴上平行air-action note的数量和其在y轴的长度有关, 默认情况下，在每间隔1.0的位置生成一个
            # 默认转换规则中，只保留最高的一个作为天键，TODO：考虑其他air-action转译为黑线
            group["type"] = "Trace"
            group["sky_end"] = True
        else:
            continue
        a_note_groups.append(group)

    # Convert the note groups to arcaea notes

    for group in a_note_groups:
        converted_notes = convert_notes_by_group(group, bpm=c_bpm)
        if len(converted_notes) > 0:
            a_notes.extend(converted_notes)

    # old version
    # for c_note in notes_list:
    #     start_time, end_time = convert_time_beats_to_ms(c_note, c_bpm, aff_audio_offset=Aff_AudioOffset)
    #
    #     # Convert chuni note to arcaea note by type.
    #     c_type = c_note[0]
    #     converted_notes = convert_note_type(c_type, start_time, end_time, c_note)
    #     if len(converted_notes) > 0:
    #         a_notes.extend(converted_notes)

    # 3. Combine timing and notes to AffList
    # a_notes.append(aff.TimingGroup(a_timing_notes))
    a_notes.extend(a_timing_notes)
    afflist = aff.AffList(a_notes)
    # afflist.offsetto(0)
    return afflist


def write_aff_file(aff_list, file_path):
    aff.dumps(aff_list, file_path)


# 使用示例
file_path = r"D:\ARC_Fanmade\Charts\ArcCreateProjects\蜘蛛丝\music2060\2060_02.c2s"  # 替换为你的文件路径
c_metadata, c_timing_list, c_notes_list = read_c2s_file(file_path)
aff_list = convert_to_aff(c_timing_list, c_notes_list)
write_aff_file(aff_list, file_path.replace('.c2s', '.aff'))
