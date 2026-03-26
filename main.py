from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
import mimetypes

app = FastAPI()

# 用来存放上传文件的目录，没有就自动创建
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 用来存剪贴板内容的简单变量（注意：重启服务就没了，但够用了）
clipboard_content = ""


@app.get("/", response_class=HTMLResponse)
async def main_page():
    '''主页，返回一个简单的HTML页面'''
    # 这个HTML我稍后会解释，你先复制
    # html_content = r""" """
    # return html_content

    _dir = os.path.dirname(os.path.abspath(__file__))
    html = os.path.join(_dir, "index.html")
    return FileResponse(html)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    '''文件上传接口'''
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    # 防止文件名冲突的小处理，这里简单覆盖同名文件
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        return {"filename": file.filename, "message": "上传成功"}


@app.get("/files")
async def list_files():
    '''获取文件列表'''
    try:
        files = os.listdir(UPLOAD_DIR)
        # 只返回文件，过滤掉目录（如果有的话）
        files = [f for f in files if os.path.isfile(
            os.path.join(UPLOAD_DIR, f))]
        return {"files": files}
    except Exception as e:
        return {"files": []}


@app.get("/download/{filename}")
async def download_file(filename: str):
    '''下载文件'''
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "文件不存在"})
    # return FileResponse(file_path, filename=filename)

    # 增加图片显示功能
    # 获取文件的MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    # 图片、PDF等想让浏览器直接显示，用 inline；其他用 attachment
    # 这里只针对常见图片类型做内联显示
    if mime_type.startswith("image/"):
        return FileResponse(file_path, media_type=mime_type, filename=filename)
    else:
        # 非图片文件，强制下载
        return FileResponse(file_path, media_type=mime_type, filename=filename, headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"})


@app.get("/clipboard")
async def get_clipboard():
    '''获取剪贴板内容'''
    return {"content": clipboard_content}


@app.post("/clipboard")
async def update_clipboard(request: Request):
    '''更新剪贴板内容'''
    global clipboard_content
    data = await request.json()
    clipboard_content = data.get("content", "")
    return {"message": "剪贴板已更新"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
