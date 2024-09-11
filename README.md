# ChuAeani
An beatmap converter from Chunithm to Arcaea fanmade.

## 特性
- 支持将Chunithm谱面`(.c2s)`转换为Arcaea谱面`(.aff)`
- 支持合并转换后的谱面，导出制谱器工程包
  - 目前支持编辑器：[ArcCreate](https://github.com/Arcthesia/ArcCreate)
  - PS：直接导入Arcade也可以使用，只不过缺少songlist和谱面信息，导出Arcade功能后续即将支持。
  - **声明：本项目仅作为工具提供，不提供也不存储任何文本与媒体资源文件，使用者自行上传的任何此类文件与本项目开发者无关。**
- 支持自定义转换设置，目前进度：
  - [x] 长条位置（地面/天空）
  - [x] 添加 AIR 黑线上箭头
  - [ ] 添加 AIR 黑线下箭头
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
  - Supported editor: [ArcCreate](https://github.com/Arcthesia/ArcCreate)
  - PS: You can also use it in Arcade, but it lacks beatmap information. Exporting to Arcade will be supported soon.
  - **Note: This project only functions as a tool, it does not provide or store any text and media resource files. The developer of this project is not responsible for any such files uploaded by the user.**
- Support custom conversion settings, implemented:
  - [x] Long note position (Ground/Sky)
  - [x] Add AIR black line upper arrow
  - [ ] Add AIR black line lower arrow
  - [x] AIR-Action style (None/Black line/Red Arc)
  - [x] Flick style (Tap/ArcTap/Blue Arc)
  - [ ] Overlapping note detection
  - [ ] Overlapping snake detection
- Future development plan
  - [ ] Generate preview image of converted beatmap
  - [ ] UMIGURI format support (not now)

## 使用说明
- 在线使用：
  - 访问[ChuAeani](https://chuaeani.streamlit.app/)
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

## 感谢
- Aff谱面处理模块来自：[arcfutil](https://github.com/feightwywx/arcfutil)
