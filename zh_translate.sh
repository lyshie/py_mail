#!/bin/sh

DOMAIN="py_mail"
ZH_PATH="I18N/zh_TW/LC_MESSAGES"
POT="$ZH_PATH/$DOMAIN.pot"
PO="$ZH_PATH/$DOMAIN.po"
MO="$ZH_PATH/$DOMAIN.mo"
SRC="./py_mail.py"

pygettext.py --output="$POT" "$SRC"

if [ ! -f "$PO" ]; then
    echo "You should copy '$POT' to '$PO' first."
    exit
fi

msgmerge --update "$PO" "$POT"

vim "$PO"

msgfmt --output-file="$MO" "$PO"
