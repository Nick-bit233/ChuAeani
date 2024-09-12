# ChuAeani
An beatmap converter from Chunithm to Arcaea fanmade.
一个简易的Chunithm转Arcaea谱面转换器

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

## 特性
- 支持将Chunithm谱面`(.c2s)`转换为Arcaea谱面`(.aff)`
- 支持合并转换后的谱面，导出制谱器工程包
  - 目前支持编辑器：[ArcCreate](https://github.com/Arcthesia/ArcCreate)、Arcade
  - PS：Arcade暂不支持直接生成songlist.txt谱面信息，请使用Arcade内置工具自行生成。
  - **声明：本项目仅作为工具提供，不提供也不存储任何文本与媒体资源文件，使用者自行上传的任何此类文件与本项目开发者无关。**
- 支持自定义转换设置，目前进度：
  - [x] 长条位置（地面/天空）
  - [x] 添加 AIR 转换后的黑线上箭头样式
  - [ ] 添加 更多 AIR 黑线样式：下箭头、向左/向右箭头等
  - [x] AIR-Action 样式（无/黑线/红色Arc）
  - [x] Flick 样式（Tap/ArcTap/蓝色Arc）
  - [ ] 重叠note检测
  - [ ] 重叠蛇检测
- 其他功能开发计划
  - [ ] 添加转换后谱面预览图生成
  - [ ] UMIGURI 格式支持 （大坑）

## Feature
- Convert Chunithm beatmap(.c2s) to Arcaea beatmap(.aff)
- Support merge converted beatmap, export aff package
  - Supported editor: [ArcCreate](https://github.com/Arcthesia/ArcCreate), Arcade
  - **Note: This project only functions as a tool, it does not provide or store any text and media resource files. The developer of this project is not responsible for any such files uploaded by the user.**
- Support custom conversion settings, implemented:
  - [x] Long note position (Ground/Sky)
  - [x] Add AIR style: upper arrow trace.
  - [ ] Add more AIR style: lower arrow trace, left / right arrow trace, etc.
  - [x] AIR-Action style (None/Traces/Red Arc)
  - [x] Flick style (Tap/ArcTap/Blue Arc)
  - [ ] Overlapping note detection
  - [ ] Overlapping arcs detection
- Future development plan
  - [ ] Generate preview image of converted beatmap
  - [ ] UMIGURI format support (not now)

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
