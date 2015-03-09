#!/bin/sh
VIRTUAL_ENV=${VIRTUAL_ENV:?virtualenv must be set}

# source directory -- same as directory where this script resides
SOURCE_DIR=${PWD}/`dirname $0`

STARS_ROOT="${SOURCE_DIR}/../.."
ln -i -s ${SOURCE_DIR}/bob.dir-locals.el ${STARS_ROOT}/.dir-locals.el

POSTACTIVATE_SCRIPT="${VIRTUAL_ENV}/bin/postactivate"

FILES_TO_SOURCE="aashe.common.postactivate bob.postactivate"
for FILE_TO_SOURCE in ${FILES_TO_SOURCE}
do
    if [ `grep -c "${SOURCE_DIR}/${FILE_TO_SOURCE}" "${POSTACTIVATE_SCRIPT}"` \
         -eq 0 ]
    then
       echo "\nsource ${SOURCE_DIR}/${FILE_TO_SOURCE}" >> ${POSTACTIVATE_SCRIPT}
       WARN_ABOUT_REACTIVATING=1
    fi
done

if [ ${WARN_ABOUT_REACTIVATING:=0} -gt 0 ]
then
    echo "deactivate then reactivate your virtualenv to pick up the postinstall hooks"
fi
