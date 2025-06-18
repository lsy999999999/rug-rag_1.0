#!/usr/bin/env python3
"""启动脚本"""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("wenshu.main:app", host="0.0.0.0", port=8080, reload=True)
