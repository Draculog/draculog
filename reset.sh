rm Newly_Executed_Code.txt
NAME="Source/name_4321"
[ -d ${NAME} ] || mv ${NAME}* ${NAME}
echo "${NAME}" > Newly_Downloaded_Code.txt
rm ${NAME}/Results.json

