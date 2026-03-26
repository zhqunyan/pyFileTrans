from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

app = FastAPI()

# 用来存放上传文件的目录，没有就自动创建
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 用来存剪贴板内容的简单变量（注意：重启服务就没了，但够用了）
clipboard_content = ""

# 主页，返回一个简单的HTML页面


@app.get("/", response_class=HTMLResponse)
async def main_page():
    # 这个HTML我稍后会解释，你先复制
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>私家传送站</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; background: #f9f9f9; }
        .card { background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        h2 { margin-top: 0; font-size: 1.5rem; }
        input, textarea, button { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        button { background-color: #3498db; color: white; border: none; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #2980b9; }
        .result { margin-top: 16px; padding: 12px; background: #f0f7ff; border-radius: 8px; font-size: 14px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📎 文件互传</h2>
        <form id="uploadForm" enctype="multipart/form-data">
            <input type="file" name="file" id="fileInput" required>
            <button type="submit">上传到电脑</button>
        </form>
        <div id="uploadResult" class="result"></div>
    </div>

    <div class="card">
        <h2>📋 剪贴板同步</h2>
        <textarea id="clipText" rows="4" placeholder="在这里粘贴或查看文本..."></textarea>
        <button id="syncToServer">📤 同步到电脑</button>
        <button id="loadFromServer">📥 从电脑获取</button>
        <div id="clipResult" class="result"></div>
    </div>

    <script>
        // 文件上传逻辑
        document.getElementById('uploadForm').onsubmit = async (e) => {
            e.preventDefault();
            const file = document.getElementById('fileInput').files[0];
            if (!file) return;
            const formData = new FormData();
            formData.append('file', file);
            const res = await fetch('/upload', { method: 'POST', body: formData });
            const data = await res.json();
            document.getElementById('uploadResult').innerHTML = `✅ ${data.filename} 上传成功`;
        };

        // 剪贴板同步
        document.getElementById('syncToServer').onclick = async () => {
            const text = document.getElementById('clipText').value;
            const res = await fetch('/clipboard', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: text }) });
            const data = await res.json();
            document.getElementById('clipResult').innerHTML = `📤 ${data.message}`;
        };

        document.getElementById('loadFromServer').onclick = async () => {
            const res = await fetch('/clipboard');
            const data = await res.json();
            document.getElementById('clipText').value = data.content;
            document.getElementById('clipResult').innerHTML = `📥 已同步: ${data.content.substring(0, 50)}`;
        };
    </script>
</body>
</html>
"""
    return html_content

# 文件上传接口


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # 防止文件名冲突的小处理，这里简单覆盖同名文件
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        return {"filename": file.filename, "message": "上传成功"}

# 获取剪贴板内容


@app.get("/clipboard")
async def get_clipboard():
    return {"content": clipboard_content}

# 更新剪贴板内容


@app.post("/clipboard")
async def update_clipboard(request: Request):
    global clipboard_content
    data = await request.json()
    clipboard_content = data.get("content", "")
    return {"message": "剪贴板已更新"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
