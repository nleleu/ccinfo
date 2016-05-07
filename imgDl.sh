#!/bin/bash

BASE_WEBSITE="http://www.campingcar-infos.com/Francais/"
HTML_DIR="html"
LOGO_PATH="../"
cd $HTML_DIR
files=$(grep -r "img.*src=\"$BASE_WEBSITE" | grep -Po "http://www.campingcar-infos.com[^\"]*" | sort -u)


for file in ${files}; do
    imgPath=${file#$BASE_WEBSITE}
    imgPath=${imgPath#$LOGO_PATH}
    dirname=$(dirname $imgPath)
    if [ -f $imgPath ]
    then
        echo "${imgPath} already dumped"
        find -type f -name '*.html' -exec sed -i "s~src=\"$file~src=\"$imgPath~g" {} \;
        continue
    fi
    echo "Dumping ${imgPath}..."
    wget -U 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20070802 SeaMonkey/1.1.4' ${file} -P ${dirname} -q
    if [ $? -ne 0 ]; then
        echo "${imgPath} : wget error"
        continue
    fi
    find -type f -name '*.html' -exec sed -i "s~src=\"$file~src=\"$imgPath~g" {} \;
done
