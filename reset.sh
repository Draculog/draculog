NAME="Source/java_trees"
EC_FILE="Newly_Executed_Code.txt"
DC_FILE="Newly_Downloaded_Code.txt"
EX_FILE="Executing_Code.txt"
RE_FILE="${NAME}/Results.json"
[ -f ${EC_FILE} ] && rm $EC_FILE
[ -d ${NAME} ] || mv ${NAME}* ${NAME}
echo "${NAME}" > $DC_FILE
[ -f $RE_FILE ] && rm $RE_FILE
[ -f $EX_FILE ] && rm $EX_FILE

