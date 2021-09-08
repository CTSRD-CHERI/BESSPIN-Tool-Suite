#!/bin/sh

TEMPLATE_DIR="templates"
CONFIGS=$(cd ${TEMPLATE_DIR}; ls)

BESSPIN_TOOL_SUITE_DIR=${BESSPIN_TOOL_SUITE_DIR:-${HOME}/BESSPIN-Tool-Suite}
CHERI_DIR=${CHERI_DIR:-${HOME}/cheri}

echo BESSPIN_TOOL_SUITE_DIR: ${BESSPIN_TOOL_SUITE_DIR}
echo CHERI_DIR: ${CHERI_DIR}
echo CONFIGS: ${CONFIGS}

for conf in $CONFIGS; do
	sed -e "s|%%BESSPIN_TOOL_SUITE_DIR%%|${BESSPIN_TOOL_SUITE_DIR}|" \
	    -e "s|%%CHERI_DIR%%|${CHERI_DIR}|" < templates/$conf > ${conf%.in}
done
