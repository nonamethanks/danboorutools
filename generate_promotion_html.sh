#!/bin/bash
WEEK_NUMBER=$(date +%Y-week-%U)
SHARE_FOLDER="/disks/disk1/share/"

mkdir -p "$SHARE_FOLDER/promotion_archives/"
poetry run promotions && cp promotions.html "$SHARE_FOLDER/promotions.html" && cp promotions.html "$SHARE_FOLDER/promotion_archives/promotions-$WEEK_NUMBER.html"
