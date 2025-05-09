#!/bin/bash
WEEK_NUMBER=$(date +%Y-week-%U)
SHARE_FOLDER="/disks/disk1/share/"
DANBOORUTOOLS_FOLDER="/home/nonamethanks/DanbooruTools"
PATH="$PATH:$HOME/.local/bin"


mkdir -p "$SHARE_FOLDER/promotion_archives/"
cd "$DANBOORUTOOLS_FOLDER" && poetry run promotions && cp promotions.html "$SHARE_FOLDER/promotions.html" && cp promotions.html "$SHARE_FOLDER/promotion_archives/promotions-$WEEK_NUMBER.html"
