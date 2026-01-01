# 图片压缩工具

一个基于Flask的单页面图片压缩应用，支持多种图片格式的上传、压缩和下载。

## 功能特点

- 支持多种图片格式：JPG, JPEG, PNG, HEIF, HEIC, WebP
- 支持多张图片同时上传和处理
- 可自定义压缩后的最大宽度和高度
- 压缩后提供实时预览和下载链接
- 下载完成后自动清理所有临时文件
- 响应式设计，支持拖放上传

## 技术实现

- **后端**：Flask框架，实现图片处理逻辑
- **前端**：HTML/CSS/JavaScript，实现用户界面和交互
- **图片处理**：
  - PIL库处理常见格式
  - heif-convert工具处理HEIF/HEIC格式
- **文件存储**：使用临时目录，自动清理机制

## 安装和运行

### 环境要求

- Python 3.7+
- libheif (系统依赖，用于处理HEIF/HEIC格式)
- heif-convert (系统依赖，用于HEIF/HEIC格式转换)

### 安装步骤

1. 克隆项目
   ```bash
   git clone https://github.com/timoseven/photo-convert.git
   cd photo-convert
   ```

2. 创建虚拟环境并安装依赖
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask pillow pyheif python-dotenv
   ```

3. 安装系统依赖（macOS）
   ```bash
   brew install libheif
   ```

4. 运行应用
   ```bash
   python app.py
   ```

5. 访问应用
   ```
   http://127.0.0.1:5000/photo/
   ```

## 使用方法

1. 拖放图片到上传区域或点击选择图片
2. 设置压缩后的最大宽度和高度
3. 点击"开始压缩"按钮
4. 压缩完成后，点击"下载"按钮获取压缩后的图片
5. 下载完成后，系统会自动清理所有临时文件

## 项目结构

```
photo-convert/
├── app.py              # Flask应用主文件
├── templates/
│   └── index.html      # 前端HTML模板
├── venv/               # 虚拟环境（忽略）
└── README.md           # 项目说明文档
```

## 路由说明

- `/photo/` - 应用主页
- `/photo/upload` - 图片上传接口
- `/photo/compress` - 图片压缩接口
- `/photo/download/<filename>` - 图片下载接口
- `/photo/cleanup` - 文件清理接口

## 许可证

MIT

## 作者

Timo & TRAE

## GitHub

https://github.com/timoseven/photo-convert
