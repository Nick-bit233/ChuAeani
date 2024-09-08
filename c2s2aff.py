import os
import re
import xml.etree.ElementTree as ET
from arcfutil import aff

# Global settings
Chuni_OffsetResolution = 384


def read_c2s_file(file_path):
    def convert_to_number(value):
        """Do the conversion to number if possible."""
        try:
            # Check if the value can be converted to an integer
            return int(value)
        except ValueError:
            try:
                # If not, check if the value can be converted to a float
                return float(value)
            except ValueError:
                # Otherwise, return the original value
                return value

    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read().strip().split('\n\n')

    # The first part of the file contains metadata
    first_part = data[0].strip().split('\n')
    metadata = {}
    for line in first_part:
        key, *values = line.split('\t')
        metadata[key] = [convert_to_number(v) for v in values]  # 转换值

    # The second part of the file contains timing information
    second_part = data[1].strip().split('\n')
    timing_list = []
    for line in second_part:
        elements = line.split('\t')
        timing_list.append([convert_to_number(e) for e in elements])  # 转换值

    # The last part of the file contains all notes info.
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

    # Try count evey partition to find the longest overlapping.
    for index, (start, end) in enumerate(partitions):
        overlap_start = max(a, start)
        overlap_end = min(b, end)

        if overlap_start < overlap_end:
            overlap_length = overlap_end - overlap_start

            if overlap_length > max_overlap_length:
                max_overlap_length = overlap_length
                best_partition_index = index

    return best_partition_index + 1


def find_note_lane_midpoint_partition(a, b):
    # 16 areas to 4k
    partitions = [(0, 4), (4, 8), (8, 12), (12, 16)]

    # Calculate the midpoint of the note
    midpoint = (a + b) / 2

    # Check if the midpoint is in any partition
    for index, (start, end) in enumerate(partitions):
        if start <= a <= end and start <= b <= end:
            return index + 1, True

    # If not, return the midpoint in float value.
    proportion = mapping_midpoint(midpoint, ground=True)

    return proportion, False

    # DYNAMIC ARC NOTE FUNC (TODO: experiment)
    # use arcaea experimental ArcTap that can shift note width to corresponding to chuni note width.


def convert_time_beats_to_ms(c_note, bpm, c_audio_betas, aff_audio_offset=0):
    audio_beats, audio_note_time = c_audio_betas[0], c_audio_betas[1]
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


def mapping_midpoint(midpoint, ground=True):
    # Arcaea ground lane is from -0.5 to 1.5, and sky lane is from 0.0 to 1.0. [FTR default]
    # TODO: add BYD setting.
    if ground:
        if midpoint < 0:
            return -0.5
        elif midpoint > 16:
            return 1.5
        else:
            proportion = midpoint / 16
            proportion = proportion * (1.5 + 0.5) - 0.5
            return proportion
    else:
        return midpoint / 16


def mapping_y_axis(c_value, c_ground=1.0, a_ground=0.0, c_sky=5.0, a_sky=1.0):
    # mapping y_axis from chuni to arcaea
    # MAX arc y set as 1.5, MIN arc y set as 0.0.
    m = (a_sky - a_ground) / (c_sky - c_ground)
    b = a_ground - m * c_ground
    if c_value > c_sky:
        return 0.67 * (m * c_value + b)
    else:
        return m * c_value + b


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


def convert_notes_by_group(group, bpm, c_audio_beats, a_audio_offset) -> list[aff.Note]:
    # Group has four types: Single, Hold, Snake, Trace
    target_notes = []

    if group["type"] == "Single":
        head_note = group["list"][0]
        start_time, end_time = convert_time_beats_to_ms(head_note, bpm, c_audio_beats, aff_audio_offset=a_audio_offset)
        note_lane_left, note_lane_width = head_note[3], head_note[4]

        # TODO: Check FLK as other builds.
        if group["sky_end"]:  # build as ArcTap
            a_note_x = mapping_midpoint(note_lane_left + note_lane_width / 2, ground=False)
            target_notes.append(
                aff.Arc(start_time, start_time + 3, a_note_x, a_note_x, 's',
                        1, 1, 0, True, [start_time]))
            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(start_time, a_note_x))

        else:
            # Mapping the note x position to Arcaea lane, for those who can't be mapped, build as ArcTap on the ground.
            a_lane, is_inside_lane = find_note_lane_midpoint_partition(note_lane_left, note_lane_left + note_lane_width)
            if is_inside_lane:
                target_notes.append(aff.Tap(start_time, a_lane))
            else:
                target_notes.append(
                    aff.Arc(start_time, start_time + 3, a_lane, a_lane, 's',
                            0, 0, 0, True, [start_time]))

    elif group["type"] == "Hold":
        head_note = group["list"][0]
        start_time, end_time = convert_time_beats_to_ms(head_note, bpm, c_audio_beats, aff_audio_offset=a_audio_offset)

        note_lane_left, note_lane_width = head_note[3], head_note[4]

        # Mapping the hold note x position to Arcaea lane, for those who is not inside a lane, find the nearest one.
        a_lane = find_note_lane_overlap_partition(note_lane_left, note_lane_left + note_lane_width)
        target_notes.append(aff.Hold(start_time, end_time, a_lane))

        if group["sky_end"]:  # Add an ArcTap at the end of the hold if the group end with AIR.
            tail_note = group["list"][1]

            a_note_x = mapping_midpoint(tail_note[3] + tail_note[4] / 2, ground=False)
            target_notes.append(
                aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
                        1, 1, 0, True, [end_time]))
            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(end_time, a_note_x))

    elif group["type"] == "Snake":
        # TODO: Combine continues slide notes to a single Arc.
        arc_head_time, arc_tail_time = -1, -1
        arc_head_x, arc_tail_x = -1, -1
        arc_direction = 0
        s_easing = 'si'  # Default easing for snake arc

        # TODO：config default y
        arc_y_default = 0
        for note in group["list"]:
            note_type = note[0]
            start_time, end_time = convert_time_beats_to_ms(note, bpm, c_audio_beats, aff_audio_offset=a_audio_offset)
            if note_type in ['AIR', 'AUL', 'AUR']:
                assert len(group["list"]) > 1, "AIR note should not be the first note in a snake group."
                # Build if the group end with an AIR
                tail_note = note
                a_note_x = mapping_midpoint(tail_note[3] + tail_note[4] / 2, ground=False)
                target_notes.append(
                    aff.Arc(end_time, end_time + 3, a_note_x, a_note_x, 's',
                            1, 1, 0, True, [end_time]))
                # Add chuni air style trace decorations.
                target_notes.extend(get_chuni_air_arrow(end_time, a_note_x))
                continue

            x_start = mapping_midpoint(note[3] + note[4] / 2, ground=True)
            x_end = mapping_midpoint(note[6] + note[7] / 2, ground=True)
            if start_time == end_time and x_start == x_end:
                continue
            if note_type in ['SXC', 'SLC']:
                this_direction = 1 if x_start < x_end else -1
                if arc_head_x == -1:
                    # This is the first note of the snake group.
                    arc_head_x = x_start
                    arc_tail_x = x_end
                    arc_head_time = start_time
                    arc_tail_time = end_time
                    arc_direction = this_direction  # Initialize the direction of the arc.
                else:
                    # Check if the arc should be cut and add a si arc
                    if arc_tail_x != x_start or arc_direction != this_direction:
                        target_notes.append(
                            aff.Arc(arc_head_time, arc_tail_time, arc_head_x, arc_tail_x, s_easing,
                                    arc_y_default, arc_y_default, 0, False, []))
                        arc_head_x = x_start
                        arc_tail_x = x_end
                        arc_head_time = start_time
                        arc_tail_time = end_time
                        arc_direction = this_direction
                        # when change direction, shift the easing type.
                        s_easing = 'so' if s_easing == 'si' else 'si'
                    else:  # continue the arc
                        arc_tail_x = x_end
                        arc_tail_time = end_time

            elif note_type in ['SXD', 'SLD']:
                if not (arc_tail_x == -1 and arc_tail_time == -1):
                    # Finish the existing SLC/SXC arc.
                    target_notes.append(
                        aff.Arc(arc_head_time, arc_tail_time, arc_head_x, arc_tail_x, s_easing,
                                arc_y_default, arc_y_default, 0, False, []))
                    # 因为已经做了以便预筛选，使得一个group中所有的slide都以SLD或SXD结尾（大概），所以这里不需要再做额外的处理。
                # Build a 's' arc for the SLD/SXD slide, whatever there are any SLC/SXC before.
                target_notes.append(
                    aff.Arc(start_time, end_time, x_start, x_end, 's',
                            arc_y_default, arc_y_default, 0, False, []))

    elif group["type"] == "Trace":
        note = group["list"][0]
        note_type = note[0]
        start_time, end_time = convert_time_beats_to_ms(note, bpm, c_audio_beats, aff_audio_offset=a_audio_offset)

        x_start = mapping_midpoint(note[3] + note[4] / 2, ground=True)
        if note_type in ['AHD', 'AHX']:  # These kind of trace does not shift the x position.
            x_end = x_start
        else:  # These kind of trace may shift the x position.
            x_end = mapping_midpoint(note[8] + note[9] / 2, ground=True)

        arc_y_default = 1.0  # Always set the y position to 1.0 if trace is not an ALD/ASD.
        arc_y_start, arc_y_end = arc_y_default, arc_y_default
        if note_type in ['ALD', 'ASD']:  # For ALD/ASD, read the y position.
            arc_y_start = mapping_y_axis(note[6])
            arc_y_end = mapping_y_axis(note[10])
            if len(note) > 11:  # Read the color if it is defined in the end of the line.
                arc_color = note[11]

        s_easing = 'si' if note_type in ['ASC'] else 's'  # Only ASC has easing 'si', others are 's'.

        if start_time == end_time and x_start == x_end and arc_y_start == arc_y_end:
            return target_notes
        # Build the trace arc.
        target_notes.append(
            aff.Arc(start_time, end_time, x_start, x_end, s_easing,
                    arc_y_start, arc_y_end, 0, True, []))

        # For AHD, ASD, AHX, a default AIR-ACTION is made at the end of the trace. Build a short-time RED ARC for it.
        # 对于 AHD ASD AHX，默认转译结尾一个长度为1/8拍的红蛇，作为air-action，TODO：提供选项改为天键
        air_action_time = 60000 / bpm / 8

        if note_type in ['AHD', 'ASD', 'AHX']:
            target_notes.append(
                aff.Arc(end_time, end_time + air_action_time, x_end, x_end, 's',
                        restrict_y_axis(arc_y_end), restrict_y_axis(arc_y_end), 1, False, []))

        # For ALD, there are maybe multiple AIR-ACTIONs on the trace, check the duration and interval time value
        # to make sure of it.
        # 对于ALD，检查持续时间和第五个值是否为间隔时间t
        if note_type == 'ALD':
            if len(note) > 7 and isinstance(note[5], int) and note[5] > 0:
                t = note[5]
                duration = note[7]
                if t < duration:
                    # For every t offset, add an air-action.
                    for i in range(t, duration, t):
                        # 时间插值
                        audio_beats = 4  # TODO： parametric this.
                        beat_duration_ms = 60000 / bpm
                        t_start = (start_time +
                                   (i / Chuni_OffsetResolution) * (audio_beats * beat_duration_ms))
                        # 位置插值  TODO：考虑红蛇的位移也进行插值
                        t_x = x_start + (x_end - x_start) * i / duration
                        t_y = restrict_y_axis(arc_y_start + (arc_y_end - arc_y_start) * i / duration)
                        target_notes.append(
                            aff.Arc(t_start, t_start + air_action_time, t_x, t_x, 's',
                                    t_y, t_y, 1, False, []))
                else:
                    # By default, add an air-action at the end of the trace.
                    t_y = restrict_y_axis(arc_y_end)
                    target_notes.append(
                        aff.Arc(end_time, end_time + air_action_time, x_end, x_end, 's',
                                t_y, t_y, 1, False, []))
                    if arc_y_start != arc_y_end:
                        # In chunithm, if an ALD have different start and end y pos, parallel air-actions will be added.
                        # We impl this feature in form of black traces by default.
                        # TODO: 添加重叠的 air-action 黑线效果
                        pass
                        # target_notes.append(get_chuni_y_air_actions(arc_x_start, arc_x_end, arc_y_start, arc_y_end))

        # Add chuni air style trace decorations if a TAP or HOLD note is followed by this trace.TODO：提供选项可添加天键
        if len(note) > 5 and note[5] in ['TAP', 'CHR', 'FLK', 'HLD', 'HXD', 'SLD']:
            # Add ArcTap note
            # target_notes.append(
            #     aff.Arc(start_time, start_time + 3, arc_start_x, arc_start_x, 's',
            #             1, 1, 0, True, [start_time]))

            # Add chuni air style trace decorations.
            target_notes.extend(get_chuni_air_arrow(start_time, x_start))
    return target_notes


def convert_to_aff(configs, c_metadata, timing_list, notes_list) -> aff.AffList:
    aff_audio_offset = configs.get("AudioOffset", 0)

    c_bpm = c_metadata["BPM_DEF"][0]  # default bpm
    c_audio_beats = c_metadata["MET_DEF"]

    # 1. Set BPM and Convert SFL timing_list to AffNote objects
    a_timing_notes = []
    sfl_end_time = 0
    c_bpms = []
    for c_timing in timing_list:
        if c_timing[0] == 'BPM':
            if c_timing[1] == 0:
                a_timing_notes.append(aff.Timing(0, c_timing[3]))
                c_bpms.append((0, c_timing[3]))
            else:
                bpm_start_time, _ = convert_time_beats_to_ms(c_timing, c_bpm,
                                                             c_audio_beats, aff_audio_offset=aff_audio_offset)
                # TODO: 中二可能定义多个时间段的不同base bpm，需要分别计算
                a_timing_notes.append(aff.Timing(0, c_bpm))
                c_bpms.append((bpm_start_time, c_bpm))
        if c_timing[0] == 'SFL':
            sfl_start_time, sfl_end_time = convert_time_beats_to_ms(c_timing, c_bpm,
                                                                c_audio_beats, aff_audio_offset=aff_audio_offset)
            a_bpm = c_bpm * float(c_timing[4])
            a_timing_notes.append(aff.Timing(sfl_start_time, a_bpm))

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
            found_D_end = True if head_note_type in ['SXD', 'SLD'] else False

            # Search for continued slide notes. SLC to SLC, end with SLD, SXC to SXC, end with SXD
            for j in range(i + 1, len(notes_list)):
                next_slide = notes_list[j]
                next_slide_type = next_slide[0]
                next_slide_head = (next_slide[3], next_slide[4])

                if not found_D_end:
                    if next_slide_type == head_note_type and next_slide_head == curr_tail:
                        group["list"].append(next_slide)
                        curr_tail = (next_slide[6], next_slide[7])
                        processed_indices.add(j)
                        continue
                    elif (next_slide_type == 'SLD' and head_note_type == 'SLC') \
                            or (next_slide_type == 'SXD' and head_note_type == 'SXC') \
                            and next_slide_head == curr_tail:
                        group["list"].append(next_slide)
                        curr_tail = (next_slide[6], next_slide[7])
                        processed_indices.add(j)
                        found_D_end = True
                        continue
                else:
                    if next_slide_type in ['AIR', 'AUL', 'AUR']:
                        end_note = next_slide
                        end_note_target = end_note[5] if len(end_note) > 5 else None
                        end_note_position = (end_note[3], end_note[4])
                        if end_note_target in ['SXD', 'SLD'] and end_note_position == curr_tail:
                            group["sky_end"] = True
                            group["list"].append(end_note)
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
        converted_notes = convert_notes_by_group(group, c_bpm, c_audio_beats, aff_audio_offset)
        if len(converted_notes) > 0:
            a_notes.extend(converted_notes)

    # 3. Combine timing and notes to AffList
    a_notes.extend(a_timing_notes)
    afflist = aff.AffList(a_notes)
    return afflist


def write_aff_file(aff_list, file_path):
    aff.dumps(aff_list, file_path)


def get_c_music_info(xml_file, c2s_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    music_name = root.find('.//name/str').text.strip()
    artist_name = root.find('.//artistName/str').text.strip()

    # 获得c2s file的文件名,去除扩展名:
    c2s_file_name = os.path.splitext(os.path.basename(c2s_file))[0]
    # 获得文件名_后的部分：
    c2s_type = c2s_file_name.split('_')[1]
    difficulty_table = ['Basic', 'Advanced', 'Expert', 'Master', 'ULTIMA', "WORLD'S END"]

    return {
        "MusicName": music_name,
        "ArtistName": artist_name,
        "DifficultyType": int(c2s_type),
        "DifficultyName": difficulty_table[int(c2s_type)],
    }





def create_acc_project(aff_list, c_metadata, configs, music_info, style='ArcCreate'):
    def sanitize_filename(filename):
        # Windows disallowed characters: \ / : * ? " < > |
        return re.sub(r'[\\/:*?"<>|]', '_', filename)

    def get_arcproj_charts_format(chart):
        return f"""chartPath: {chart["chartPath"]}
  audioPath: {chart["audioPath"]}
  jacketPath: {chart["jacketPath"]}
  baseBpm: {chart["baseBpm"]}
  bpmText: {chart["bpmText"]}
  syncBaseBpm: {chart["syncBaseBpm"]}
  title: {chart["title"]}
  composer: {chart["composer"]}
  charter: {chart["charter"]}
  alias: {chart["alias"]}
  illustrator: {chart["illustrator"]}
  difficulty: {chart["difficulty"]}
  difficultyColor: {chart["difficultyColor"]}
  lastWorkingTiming: {chart["lastWorkingTiming"]}
  previewEnd: {chart["previewEnd"]}\n"""

    creator_string = c_metadata["CREATOR"][0]
    c_bpm = c_metadata["BPM_DEF"][0]

    if configs["AffProjectName"] != "":
        arcproj_name = configs["AffProjectName"]
    else:
        arcproj_name = music_info['MusicName']

    # Sanitize the arcproj_name
    arcproj_name = sanitize_filename(arcproj_name)

    arcproj_path = configs["AffProjectDirPath"]
    aff_difficulty_type = music_info["DifficultyType"] if music_info["DifficultyType"] < 4 else 4

    # Check if arcproj_path exists, if not, create it.
    if not os.path.exists(arcproj_path):
        os.makedirs(arcproj_path)

    # Check if base.ogg exists, if not, create it.
    if not os.path.exists(os.path.join(arcproj_path, "base.ogg")):
        with open(os.path.join(arcproj_path, "base.ogg"), "w") as file:
            pass

    # Check if base.png exists, if not, create it.
    if not os.path.exists(os.path.join(arcproj_path, "base.jpg")):
        with open(os.path.join(arcproj_path, "base.jpg"), "w") as file:
            pass

    # Create a Aff file:
    write_aff_file(aff_list, os.path.join(arcproj_path, f"{aff_difficulty_type}.aff"))

    if style == 'ArcCreate':
        # Create a ArcCreate project config
        arcproj_config = {
            "chartPath": f"{aff_difficulty_type}.aff",
            "audioPath": "base.ogg",
            "jacketPath": "base.jpg",
            "baseBpm": c_bpm,
            "bpmText": f"{c_bpm}",
            "syncBaseBpm": "true",
            "title": music_info["MusicName"],
            "composer": music_info["ArtistName"],
            "charter": f"{creator_string}",
            "alias": "Converted by AirARChuni version 0.1. Please be advised that this beatmap is not intended for "
                     "using in any public forum.",
            "illustrator": "\'\'",
            "difficulty": music_info["DifficultyName"],
            "difficultyColor": "\'#482B54FF\'",
            "lastWorkingTiming": 0,
            "previewEnd": 5000,
        }
        # Write .arcproj file:
        f = os.path.join(arcproj_path, f"{arcproj_name}.arcproj")
        if os.path.exists(f):
            # check if chartPath in the file, if not, append it.
            if not any(arcproj_config["chartPath"] in line for line in open(f)):
                with open(f, "a") as file:
                    file.write(f"- {get_arcproj_charts_format(arcproj_config)}")
        else:
            with open(os.path.join(arcproj_path, f"{arcproj_name}.arcproj"), "w") as file:
                file.write(f"lastOpenedChartPath: {arcproj_config['chartPath']}\n")
                file.write(f"charts:\n- {get_arcproj_charts_format(arcproj_config)}")

    elif style == 'Arcade':
        pass
    else:
        raise ValueError(f"Unsupported project style: {style}")

    return arcproj_path


def make_arcaea_project(aff_list, configs, c_metadata, style='ArcCreate'):
    if configs["MusicInfoFilePath"] and configs["MusicInfoFilePath"].endswith('.xml'):
        music_info = get_c_music_info(configs["MusicInfoFilePath"], configs["FilePath"])
    else:
        music_info = {
            "MusicName": configs["MusicName"],
            "ArtistName": configs["ArtistName"],
            "DifficultyType": configs["DifficultyType"],
            "DifficultyName": configs["DifficultyName"],
        }
    # Make Project files
    p_path = create_acc_project(aff_list, c_metadata, configs, music_info, style=style)

    # make os open the project folder
    os.startfile(p_path)


def exec_convert(configs):
    file_path = configs["FilePath"]
    c_metadata, c_timing_list, c_notes_list = read_c2s_file(file_path)
    aff_list = convert_to_aff(configs, c_metadata, c_timing_list, c_notes_list)
    # write_aff_file(aff_list, file_path.replace('.c2s', '.aff'))
    make_arcaea_project(aff_list, configs, c_metadata, style=configs["AffProjectStyle"])


# 使用示例
configs = {
    "FilePath": r"",
    "MusicInfoFilePath": r"",
    "AudioOffset": 0,
    "MusicName": "",
    "ArtistName": "",
    "DifficultyType": 2,
    "DifficultyName": "Master",
    "AffProjectDirPath": r"",
    "AffProjectStyle": "ArcCreate",
    "AffProjectName": "",
    "ConvertConfigs": {
        "check_note_overlapping": False,
    }
}
exec_convert(configs)
