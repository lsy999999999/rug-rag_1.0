import requests

with open("/home/lsyedith/ruc-rag/empty_list_filled.docx", "rb") as f1, open("/home/lsyedith/ruc-rag/test_file.docx", "rb") as f2:
    # 你的代码
    files = {
        "file": ("empty_list_filled.docx", f1, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "data_file": ("test_file.docx", f2, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    }
    resp = requests.post("http://localhost:8080/auto_fill_form", files=files)
    print(resp.json())