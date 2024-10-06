# <img src="https://github.com/user-attachments/assets/8ef6b3a1-8d14-4ea5-8c5a-568404db35fc" width="64"> ChuAeani
An beatmap converter from Chunithm to Arcaea fanmade.

一个简易的Chunithm转Arcaea谱面转换器

欢迎加入开发/使用讨论QQ群：994702414
# 最近更新
- 2024.9.22
  - 可自定义 Slide、Flick、AIR、AIR-Hold、AIR-Action 转换为蛇的颜色，支持转换为紫蛇（红蓝重叠以代替手序识别）
  - 支持更多 AIR 转换选项（上滑蛇替代天键）
  - 支持更多 AIR-Hold 转换样式（无/黑线/蛇）


- 2024.9.17 
  - 初版更新
  - 视频演示 / Preview Video : [bilibiili](https://www.bilibili.com/video/BV1Lk4DehE6V/)
  ![image](https://github.com/user-attachments/assets/7a35259e-5190-4082-afe0-fd30435a3878)
  ![image](https://github.com/user-attachments/assets/255cdd2e-9ab5-4ca1-9161-5908cfb15178)
  ![image](https://github.com/user-attachments/assets/77670f26-0821-4aa9-abfd-7e5a570fddd1)
  ![image](https://github.com/user-attachments/assets/0d85c62e-4a8b-4d61-838b-6aba131f80ef)


## 使用说明
- 在线使用：
  - 访问 [ChuAeani](https://chuaeani.streamlit.app/)
- 本地运行： 
  - 下载仓库到本地。
  - 安装依赖（建议使用python虚拟环境）：`pip install -r requirements.txt`。
  - 运行`streamlit run .\run_streamlit.py`，在弹出的浏览器页面中使用。

## Usage
- Online:
  - Visit [ChuAeani](https://chuaeani.streamlit.app/)
- Local:
  - Download the repository.
  - Install dependencies (It is recommended to use a python virtual environment): `pip install -r requirements.txt`.
  - Run `streamlit run .\run_streamlit.py`, and enjoy it in the popped up browser page.
 
## 常见问题
Q：如何找到`.c2s`文件？

A: 通常位于类似`root/app/data/AXXX/music/musicXXXX/`的目录下，该回答参考自[Chunithm-Research](https://github.com/Suprnova/Chunithm-Research/blob/main/Charting.md)

Q：转换后的谱面没有音频/曲绘？

A：如果在转换页面没有上传音频或曲绘，得到的谱面包中为空文件，请自行替换为可用资源。

Q：转换后的谱面与音频对不上？

A：可能使用的音频开始时间存在错位。请在编辑器中自行校对第一个音（或第一个小节）的开始时间，与实际谱面第一个音符的开始时间，将二者差值（ms）填入 `音频偏移` / `AudioOffset` 选项，重新转换即可。

## Q&A
Q: How to find the `.c2s` file?

A: Usually located in directories like `root/app/data/AXXX/music/musicXXXX/`, this answer is from [Chunithm-Research](https://github.com/Suprnova/Chunithm-Research/blob/main/Charting.md)

Q: The converted beatmap has no audio/cover?

A: If no audio or cover is uploaded on the conversion page, the generated beatmap package will be empty. Please replace it with available resources.

Q: The converted beatmap does not match the audio?

A: The audio start time may be misaligned. Please manually check the start time of the first note (or the first measure) in the editor, and the actual start time of the first note in the beatmap, fill the difference (ms) into the `AudioOffset` option, and reconvert.

## 特性
- 支持将Chunithm谱面`(.c2s)`转换为Arcaea谱面`(.aff)`
- 支持合并转换后的谱面，导出制谱器工程包
  - 目前支持编辑器：[ArcCreate](https://github.com/Arcthesia/ArcCreate)、Arcade
  - PS：Arcade暂不支持直接生成songlist.txt谱面信息，请使用Arcade内置工具自行生成。
  - **声明：本项目仅作为工具提供，不提供也不存储任何文本与媒体资源文件，使用者自行上传的任何此类文件与本项目开发者无关。**
- 支持自定义转换设置，目前进度：
  - [x] Slide垂直位置选项（地面/天空）
  - [x] 可将Slide转换为紫蛇（红蓝重叠以代替手序识别）
  - [x] 可将AIR-Hold转换为紫蛇
  - [x] 为转换后的 AIR 添加黑线上箭头装饰
  - [ ] 增加更多可选的 AIR 黑线装饰样式：下箭头、向左/向右箭头等
  - [x] 更多 AIR 转换选项（如上滑蛇替代天键）
  - [x] 可选 AIR-Action 转换样式（无/黑线/蛇）
  - [x] 可选 Flick 转换样式（Tap/ArcTap/碎蛇）
  - [ ] 可将长度大于2的类Tap键型转换为`HIVEMIND INTERLINKED`中出现的变长天键
  - [ ] 重叠note检测和自动筛除
  - [ ] 重叠Hold/Slide蛇检测和自动筛除
- 其他功能开发计划
  - [ ] 添加转换后谱面预览图生成
  - [ ] UMIGURI 格式支持 （大坑）

## Feature
- Convert Chunithm beatmap(.c2s) to Arcaea beatmap(.aff)
- Support merge converted beatmap, export aff package
  - Supported editor: [ArcCreate](https://github.com/Arcthesia/ArcCreate), Arcade
  - **Note: This project only functions as a tool, it does not provide or store any text and media resource files. The developer of this project is not responsible for any such files uploaded by the user.**
- Support custom conversion settings, implemented:
  - [x] Slide vertical position option (Ground/Sky)
  - [x] Convert Slide to purple Arc (red and blue overlap to let Arceae ignore hand recognition)
  - [x] Convert AIR-Hold to purple Arc
  - [x] Add black traces and arrow decorations to converted AIR
  - [ ] Add more optional AIR black trace decoration styles: down arrow, left/right arrow, etc.
  - [x] More AIR conversion options (e.g. up slide Arc instead of ArcTap)
  - [x] Optional AIR-Action conversion style (none/Traces/different Arcs)
  - [x] Optional Flick conversion style (Tap/ArcTap/different Arcs)
  - [ ] Convert Tap-like note whose width longer than 2 to the variable-length ArcTap showing in `HIVEMIND INTERLINKED`
  - [ ] Overlapping note detection and automatic filtering
  - [ ] Overlapping Hold/Arc detection and automatic filtering
- Future work
  - [ ] Generate preview image of converted beatmap
  - [ ] UMIGURI format support (maybe)

## 已知问题
  - [ ] 对于部分特殊变速和节拍谱面，小节线、timing和音符可能错位（例如：白庭、竹）
  - [ ] 部分谱面的AIR / AIR Hold不能被正确识别和翻译

如果你发现有更多谱面产生类似问题，或兴趣修复代码来贡献本仓库，欢迎issue或提供pull request。

## Known Issues
  - [ ] For some special beatmaps, beat lines, timing and notes may be misaligned (e.g. 白庭、竹)
  - [ ] AIR / AIR Hold notes of some beatmaps cannot be correctly recognized and translated

If you are interested in fixing these issues or contributing to this repository, feel free to issue or provide a pull request.

## 感谢
- Aff谱面处理模块来自：[arcfutil](https://github.com/feightwywx/arcfutil)
- Chunithm谱面格式解析来自：[Chunithm-Research](https://github.com/Suprnova/Chunithm-Research/blob/main/Charting.md)
