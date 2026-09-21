import os
import tempfile

# 必须在导入 app 之前指向独立数据目录，避免污染开发库。
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="taximeter-test-"))
