from flask import Flask, request, render_template, send_file, jsonify
import os
from PIL import Image
import pyheif
import tempfile
import shutil
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'heif', 'heic', 'webp'}

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def compress_image(input_path, output_path, max_width, max_height):
    """压缩图片到指定大小"""
    import subprocess
    try:
        # 获取原始文件扩展名
        ext = os.path.splitext(input_path)[1].lower()
        
        # 如果是HEIF/HEIC格式，使用heif-convert转换，然后使用PIL压缩
        if ext in ['.heif', '.heic']:
            # 创建临时JPEG文件
            temp_jpeg = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{os.path.basename(output_path)}.jpg")
            
            # 使用heif-convert将HEIF/HEIC转换为JPEG
            subprocess.run([
                'heif-convert',
                '-q', '85',  # 质量设置
                input_path,  # 输入文件
                temp_jpeg  # 输出临时JPEG文件
            ], check=True, capture_output=True, text=True)
            
            # 使用PIL打开转换后的JPEG文件并压缩
            img = Image.open(temp_jpeg)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            img.save(output_path, optimize=True, quality=85)
            
            # 删除临时文件
            os.remove(temp_jpeg)
        else:
            # 对于其他格式，直接使用PIL进行压缩
            img = Image.open(input_path)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            img.save(output_path, optimize=True, quality=85)
    except subprocess.CalledProcessError as e:
        raise Exception(f"图片压缩失败: {e.stderr}")
    except Exception as e:
        raise Exception(f"图片压缩失败: {str(e)}")

def cleanup_files(files):
    """清理文件"""
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """处理图片上传"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files part'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    uploaded_files = []
    for file in files:
        if file and allowed_file(file.filename):
            # 保存文件到临时目录，使用UUID确保唯一性
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            timestamp = str(int(datetime.now().timestamp()))
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_{timestamp}_{unique_id}_{file.filename}")
            file.save(temp_path)
            uploaded_files.append({
                'filename': file.filename,
                'path': temp_path,
                'original_size': os.path.getsize(temp_path)
            })
    
    return jsonify({'files': uploaded_files})

@app.route('/compress', methods=['POST'])
def compress_files():
    """处理图片压缩"""
    data = request.get_json()
    if not data or 'files' not in data or 'max_width' not in data or 'max_height' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    files = data['files']
    max_width = int(data['max_width'])
    max_height = int(data['max_height'])
    
    compressed_files = []
    for file_data in files:
        input_path = file_data['path']
        filename = file_data['filename']
        
        # 创建压缩后的文件名，确保能清晰关联到原始图片
        name, ext = os.path.splitext(filename)
        
        # 如果是HEIF/HEIC格式，压缩后使用.jpg扩展名
        if ext.lower() in ['.heif', '.heic']:
            compressed_filename = f"{name}_compressed.jpg"
        else:
            compressed_filename = f"{name}_compressed{ext}"
            
        # 确保文件名唯一
        counter = 1
        base_name, base_ext = os.path.splitext(compressed_filename)
        temp_filename = compressed_filename
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        while os.path.exists(output_path):
            temp_filename = f"{base_name}_{counter}{base_ext}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            counter += 1
        
        compressed_filename = temp_filename
        
        # 压缩图片
        compress_image(input_path, output_path, max_width, max_height)
        
        compressed_files.append({
            'original_filename': filename,
            'compressed_filename': compressed_filename,
            'original_path': input_path,
            'compressed_path': output_path,
            'original_size': file_data['original_size'],
            'compressed_size': os.path.getsize(output_path)
        })
    
    return jsonify({'compressed_files': compressed_files})

@app.route('/download/<filename>')
def download_file(filename):
    """下载压缩后的图片"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    # 发送文件给用户下载
    return send_file(file_path, as_attachment=True)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """清理上传和压缩后的文件"""
    data = request.get_json()
    if not data or 'files' not in data:
        return jsonify({'error': 'Invalid request data'}), 400
    
    files_to_clean = []
    for file_data in data['files']:
        if 'original_path' in file_data:
            files_to_clean.append(file_data['original_path'])
        if 'compressed_path' in file_data:
            files_to_clean.append(file_data['compressed_path'])
    
    # 清理文件
    cleanup_files(files_to_clean)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)