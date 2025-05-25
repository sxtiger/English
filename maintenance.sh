#!/bin/bash
# maintenance_fixed.sh

echo "=== 开始系统维护 ==="

# 1. 清理会话文件
set -euo pipefail  # 开启严格模式

SESSION_DIR="./flask_sessions"
LOG_FILE="./maintenance.log"

echo "[$(date)] 开始维护流程" | tee -a ${LOG_FILE}

# 清理会话文件
echo "正在清理会话文件..." | tee -a ${LOG_FILE}
find "${SESSION_DIR}" -type f -mtime +0 -print -delete | tee -a ${LOG_FILE}

# 验证清理结果
remaining_files=$(find "${SESSION_DIR}" -type f | wc -l)
echo "剩余会话文件数：${remaining_files}" | tee -a ${LOG_FILE}

echo "[$(date)] 维护完成" | tee -a ${LOG_FILE}
# 2. 备份数据文件（关键修复部分）
backup_root="./backups"
year_month=$(date +%Y-%m)  # 格式改为2023-05
day=$(date +%d)
backup_dir="${backup_root}/${year_month}"

# 确保目录存在
mkdir -p "$backup_dir" || {
    echo "无法创建备份目录：${backup_dir}"
    exit 1
}

# 备份文件
cp -v "English Phrase.xlsx" "${backup_dir}/vocab_$(date +%Y%m%d).xlsx"

# 3. 清理旧备份（保留30天）
find "$backup_root" -name "*.xlsx" -mtime +30 -exec rm -v {} \;

echo "=== 维护完成 ==="

# 4. 检查依赖更新
echo "=== 检查过期依赖 ==="
echo "需手动升级的包："
pip list --outdated | grep -E 'flask|pandas|openpyxl'

echo "=== 建议操作 ==="
echo "1. 升级单个包：pip install <包名> --upgrade"
echo "2. 升级所有包：pip install -r requirements_upgrade.txt"

echo "=== 维护完成 ==="