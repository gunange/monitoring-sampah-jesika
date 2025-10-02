#!/bin/bash

read -p "Modul lama: " OLD
read -p "Modul baru: " NEW
read -p "Pertahankan modul lama? (y/n): " KEEP

echo "Modul lama: $OLD"
echo "Modul baru: $NEW"
echo "Pertahankan modul lama? (y/n): $KEEP"

MODULE_PATH=$(find src/ -type d -name "$OLD" -print -quit)

if [ -z "$MODULE_PATH" ]; then
  echo "❌ Modul '$OLD' tidak ditemukan di dalam folder src/"
  exit 1
fi

echo "🛠️ Menyalin dari modul '$OLD' ke modul '$NEW'..."
TEMP=temp_rename_$RANDOM
mkdir -p "$TEMP"

# Copy the entire module directory
cp -r "$MODULE_PATH" "$TEMP/$NEW"

# Copy additional files and folders containing $OLD in their names (case-insensitive)
find src/ -maxdepth 1 -type f -iname "*$OLD*" -exec cp {} "$TEMP/" \;
find src/ -maxdepth 1 -type d -iname "*$OLD*" ! -name "$OLD" -exec cp -r {} "$TEMP/" \;

# Rename files and directories inside the temp folder from $OLD to $NEW (case-sensitive)
find "$TEMP" -depth | grep "$OLD" | sort -r | while read OLDNAME; do
  BASENAME=$(basename "$OLDNAME")
  DIRNAME=$(dirname "$OLDNAME")

  if [[ "$BASENAME" =~ ^$OLD$ ]]; then
    # Jika nama persis sama dengan OLD
    NEWNAME="$DIRNAME/$NEW"
  elif [[ "$BASENAME" =~ ^$OLD ]]; then
    # Jika nama diawali OLD (misal: StafRepo)
    NEWNAME="$DIRNAME/${NEW}${BASENAME#$OLD}"
  elif [[ "$BASENAME" =~ $OLD$ ]]; then
    # Jika nama diakhiri OLD (misal: RepoStaf)
    NEWNAME="$DIRNAME/${BASENAME%$OLD}$NEW"
  else
    # Tidak cocok, tetap pakai ganti biasa
    NEWNAME="$DIRNAME/$(echo "$BASENAME" | sed "s/$OLD/$NEW/gI")"
  fi

  mv "$OLDNAME" "$NEWNAME"
done

echo "📁 Memindahkan hasil dari '$TEMP' ke src/..."
cp -R "$TEMP/"* src/
rm -rf "$TEMP"

# Rename file/folder di src/ yang masih mengandung $OLD (termasuk PetugasValidate.ts, PetugasRepo, dll)
find src/ -depth | grep -i "$OLD" | sort -r | while read OLDNAME; do
  BASENAME=$(basename "$OLDNAME")
  DIRNAME=$(dirname "$OLDNAME")

  if [[ "$BASENAME" =~ ^$OLD$ ]]; then
    # Jika nama persis sama dengan OLD
    NEWNAME="$DIRNAME/$NEW"
  elif [[ "$BASENAME" =~ ^$OLD ]]; then
    # Jika nama diawali OLD (misal: StafRepo)
    NEWNAME="$DIRNAME/${NEW}${BASENAME#$OLD}"
  elif [[ "$BASENAME" =~ $OLD$ ]]; then
    # Jika nama diakhiri OLD (misal: RepoStaf)
    NEWNAME="$DIRNAME/${BASENAME%$OLD}$NEW"
  else
    # Tidak cocok, tetap pakai ganti biasa
    NEWNAME="$DIRNAME/$(echo "$BASENAME" | sed "s/$OLD/$NEW/gI")"
  fi

  if [ -e "$OLDNAME" ]; then
    mkdir -p "$(dirname "$NEWNAME")"
    mv "$OLDNAME" "$NEWNAME"
  else
    echo "⚠️ Lewati, tidak ditemukan: $OLDNAME"
  fi
done

OLD_CAP=$(echo "${OLD:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${OLD:1}")
NEW_CAP=$(echo "${NEW:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${NEW:1}")
OLD_UP=$(echo "$OLD" | tr '[:lower:]' '[:upper:]')
NEW_UP=$(echo "$NEW" | tr '[:lower:]' '[:upper:]')

grep -ril "$OLD" src/ | while read file; do
  sed -i '' -e "s/$OLD_CAP/$NEW_CAP/g" -e "s/$OLD/$NEW/gI" -e "s/$OLD_UP/$NEW_UP/g" "$file"
done

if [[ "$KEEP" =~ ^[Nn]$ ]]; then
  echo "🗑️ Menghapus modul lama '$OLD'..."
  find src/ -depth -name "*$OLD*" -exec rm -rf {} +
fi

echo "✅ Modul '$OLD' berhasil disalin ke '$NEW'"
