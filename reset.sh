NAME="Source/test_238"
EC_FILE="Newly_Executed_Code.txt"
DC_FILE="Newly_Downloaded_Code.txt"
RE_FILE="${NAME}/Results.json"
[ -f ${EC_FILE} ] && rm $EC_FILE
[ -d ${NAME} ] || mv ${NAME}* ${NAME}
echo "${NAME}" > $DC_FILE
[ -f $RE_FILE ] && rm $RE_FILE

