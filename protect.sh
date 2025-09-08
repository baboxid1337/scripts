#!/bin/bash
# =======================================================
#  SSH FILE PROTECTOR v1.0 by Babox
#  Mode: User (Non-root)
# =======================================================

green="\e[32m"
yellow="\e[33m"
red="\e[31m"
end="\e[0m"

backup_dir="$HOME/.protected_files"
mkdir -p "$backup_dir"

clear
echo -e "${green}===============================================${end}"
echo -e "${yellow}        SSH FILE PROTECTOR v1.0 (User) ${end}"
echo -e "${green}===============================================${end}"

# Input file
echo -ne "${yellow}Masukkan path file yang mau diamankan: ${end}"
read filepath

# Cek file ada atau tidak
if [[ ! -f "$filepath" ]]; then
    echo -e "${red}❌ File tidak ditemukan: $filepath${end}"
    exit 1
fi

# Backup file sebelum proteksi
cp "$filepath" "$backup_dir/"
echo -e "${green}📦 Backup disimpan di: $backup_dir/$(basename "$filepath")${end}"

# Lock file (read-only)
chmod 444 "$filepath"
echo -e "${green}✅ File berhasil diamankan: $filepath${end}"

# Tambahkan alias rm anti-delete
if ! grep -q "alias rm=" ~/.bashrc; then
    echo "alias rm='echo -e \"${red}⚠️ Tidak bisa hapus file! Gunakan unlock dulu.${end}\"'" >> ~/.bashrc
    source ~/.bashrc
    echo -e "${yellow}⚠️ Fitur anti-delete diaktifkan.${end}"
fi

echo -e "\n${green}✅ Proteksi selesai!${end}"
echo -e "Kalau mau unlock, jalankan: ${yellow}chmod 644 $filepath${end}"
echo -e "Kalau mau restore backup: ${yellow}cp $backup_dir/$(basename "$filepath") $filepath${end}"
